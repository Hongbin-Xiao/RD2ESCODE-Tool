#include <reg51.h>

// 硬件引脚定义
sbit SDA = P1^0;        // I2C数据线
sbit SCL = P1^1;        // I2C时钟线
sbit LED_MANUAL = P1^2; // 手动模式LED
sbit LED_AUTO = P1^3;   // 自动模式LED

sbit KEY_MODE = P3^5;   // 模式切换按键
sbit KEY_UP = P3^0;     // 上键
sbit KEY_DOWN = P3^1;   // 下键
sbit KEY_LEFT = P3^2;   // 左键
sbit KEY_RIGHT = P3^3;  // 右键

// 全局变量定义
unsigned char mode = 0;              // 0=手动模式, 1=自动模式
unsigned char sensor_error = 0;     // 传感器错误标志
unsigned char light_values[4];      // 光敏电阻值数组
unsigned char step_phase_v = 0;     // 垂直电机相位
unsigned char step_phase_h = 0;     // 水平电机相位
unsigned char timer_count = 0;      // 定时器计数
unsigned char led_flash_count = 0;  // LED闪烁计数

// 步进电机相位表
unsigned char code vertical_forward[] = {0x01, 0x03, 0x02, 0x06, 0x04, 0x0C, 0x08, 0x09};
unsigned char code vertical_backward[] = {0x09, 0x08, 0x0C, 0x04, 0x06, 0x02, 0x03, 0x01};
unsigned char code horizontal_forward[] = {0x10, 0x30, 0x20, 0x60, 0x40, 0xC0, 0x80, 0x90};
unsigned char code horizontal_backward[] = {0x90, 0x80, 0xC0, 0x40, 0x60, 0x20, 0x30, 0x10};

// 函数声明
void system_init(void);
void delay_us(unsigned char us);
void delay_ms(unsigned char ms);
void i2c_start(void);
void i2c_stop(void);
void i2c_write_byte(unsigned char dat);
unsigned char i2c_read_byte(void);
unsigned char read_adc_channel(unsigned char channel);
void read_all_sensors(void);
void check_sensor_error(void);
void scan_keys(void);
void motor_control(unsigned char direction);
void auto_tracking(void);
void update_led_status(void);
void timer0_isr(void) interrupt 1;

// 系统初始化
void system_init(void) {
    // 配置定时器0 (2.5ms中断)
    TMOD = 0x01;    // 定时器0工作模式1
    TH0 = 0xF6;     // 12MHz晶振下2.5ms定时初值
    TL0 = 0x3C;
    ET0 = 1;        // 使能定时器0中断
    TR0 = 1;        // 启动定时器0
    EA = 1;         // 开总中断
    
    // 初始化I/O口
    P2 = 0x00;      // 步进电机控制口清零
    LED_MANUAL = 1; // 默认手动模式
    LED_AUTO = 0;
    
    mode = 0;       // 默认手动模式
    sensor_error = 0;
}

// 微秒级延时
void delay_us(unsigned char us) {
    while(us--) {
        _nop_();
        _nop_();
    }
}

// 毫秒级延时
void delay_ms(unsigned char ms) {
    unsigned char i;
    while(ms--) {
        for(i = 0; i < 120; i++) {
            delay_us(1);
        }
    }
}

// I2C起始信号
void i2c_start(void) {
    SDA = 1;
    SCL = 1;
    delay_us(5);
    SDA = 0;
    delay_us(5);
    SCL = 0;
}

// I2C停止信号
void i2c_stop(void) {
    SDA = 0;
    SCL = 1;
    delay_us(5);
    SDA = 1;
    delay_us(5);
}

// I2C写字节
void i2c_write_byte(unsigned char dat) {
    unsigned char i;
    for(i = 0; i < 8; i++) {
        SCL = 0;
        delay_us(2);
        SDA = (dat & 0x80) ? 1 : 0;
        dat <<= 1;
        delay_us(2);
        SCL = 1;
        delay_us(5);
    }
    SCL = 0;
    delay_us(2);
    SDA = 1;
    delay_us(2);
    SCL = 1;
    delay_us(5);
    SCL = 0;
}

// I2C读字节
unsigned char i2c_read_byte(void) {
    unsigned char i, dat = 0;
    SDA = 1;
    for(i = 0; i < 8; i++) {
        SCL = 0;
        delay_us(5);
        SCL = 1;
        delay_us(2);
        dat <<= 1;
        if(SDA) dat |= 0x01;
        delay_us(3);
    }
    SCL = 0;
    delay_us(2);
    SDA = 0;  // ACK
    delay_us(2);
    SCL = 1;
    delay_us(5);
    SCL = 0;
    return dat;
}

// 读取ADC指定通道
unsigned char read_adc_channel(unsigned char channel) {
    unsigned char result;
    
    i2c_start();
    i2c_write_byte(0x90);  // PCF8591写地址
    i2c_write_byte(0x40 | channel);  // 通道选择
    i2c_stop();
    
    delay_ms(1);  // 转换延时
    
    i2c_start();
    i2c_write_byte(0x91);  // PCF8591读地址
    result = i2c_read_byte();
    i2c_stop();
    
    return result;
}

// 读取所有传感器数据
void read_all_sensors(void) {
    light_values[0] = read_adc_channel(0);  // 下方
    light_values[1] = read_adc_channel(1);  // 上方
    light_values[2] = read_adc_channel(2);  // 右方
    light_values[3] = read_adc_channel(3);  // 左方
}

// 检查传感器异常
void check_sensor_error(void) {
    unsigned char i, error_flag = 0;
    
    for(i = 0; i < 4; i++) {
        if(light_values[i] == 0 || light_values[i] == 255) {
            error_flag = 1;
            break;
        }
    }
    
    sensor_error = error_flag;
}

// 按键扫描
void scan_keys(void) {
    static unsigned char key_state = 0xFF;
    unsigned char current_keys;
    
    // 读取按键状态
    current_keys = (P3 & 0x3F) | ((KEY_MODE == 0) ? 0x00 : 0x20);
    
    // 按键去抖处理
    if(current_keys != key_state) {
        delay_ms(10);
        current_keys = (P3 & 0x3F) | ((KEY_MODE == 0) ? 0x00 : 0x20);
        
        if(current_keys == key_state) {
            return;
        }
        
        // 模式切换键
        if((key_state & 0x20) && !(current_keys & 0x20)) {
            mode = !mode;
        }
        
        // 手动控制键（仅在手动模式下有效）
        if(mode == 0 && sensor_error == 0) {
            if((key_state & 0x01) && !(current_keys & 0x01)) {
                motor_control(1);  // 上
            }
            if((key_state & 0x02) && !(current_keys & 0x02)) {
                motor_control(2);  // 下
            }
            if((key_state & 0x04) && !(current_keys & 0x04)) {
                motor_control(3);  // 左
            }
            if((key_state & 0x08) && !(current_keys & 0x08)) {
                motor_control(4);  // 右
            }
        }
        
        key_state = current_keys;
    }
}

// 电机控制
void motor_control(unsigned char direction) {
    unsigned char motor_code = 0;
    
    switch(direction) {
        case 1: // 上 - 垂直正转
            motor_code = vertical_forward[step_phase_v];
            step_phase_v++;
            if(step_phase_v >= 8) step_phase_v = 0;
            break;
            
        case 2: // 下 - 垂直反转
            motor_code = vertical_backward[step_phase_v];
            step_phase_v++;
            if(step_phase_v >= 8) step_phase_v = 0;
            break;
            
        case 3: // 左 - 水平反转
            motor_code = horizontal_backward[step_phase_h];
            step_phase_h++;
            if(step_phase_h >= 8) step_phase_h = 0;
            break;
            
        case 4: // 右 - 水平正转
            motor_code = horizontal_forward[step_phase_h];
            step_phase_h++;
            if(step_phase_h >= 8) step_phase_h = 0;
            break;
            
        default:
            return;
    }
    
    P2 = motor_code;
    delay_ms(3);  // 确保步进电机稳定转动
}

// 自动跟踪算法
void auto_tracking(void) {
    signed char diff_vertical, diff_horizontal;
    
    if(mode != 1 || sensor_error != 0) {
        return;
    }
    
    // 计算垂直方向光强差值 (上方 - 下方)
    diff_vertical = (signed char)light_values[1] - (signed char)light_values[0];
    
    // 计算水平方向光强差值 (右方 - 左方)
    diff_horizontal = (signed char)light_values[2] - (signed char)light_values[3];
    
    // 垂直方向调整
    if(diff_vertical >= 15) {
        motor_control(1);  // 向上调整
    } else if(diff_vertical <= -15) {
        motor_control(2);  // 向下调整
    }
    
    // 水平方向调整
    if(diff_horizontal >= 15) {
        motor_control(4);  // 向右调整
    } else if(diff_horizontal <= -15) {
        motor_control(3);  // 向左调整
    }
}

// 更新LED状态
void update_led_status(void) {
    if(sensor_error) {
        // 异常状态 - 双LED闪烁 (1Hz)
        if(led_flash_count >= 100) {  // 约1秒
            LED_MANUAL = !LED_MANUAL;
            LED_AUTO = LED_MANUAL;
            led_flash_count = 0;
        }
    } else {
        // 正常状态 - 根据模式显示
        if(mode == 0) {
            LED_MANUAL = 1;
            LED_AUTO = 0;
        } else {
            LED_MANUAL = 0;
            LED_AUTO = 1;
        }
    }
}

// 定时器0中断服务程序 (2.5ms)
void timer0_isr(void) interrupt 1 {
    TH0 = 0xF6;  // 重装初值
    TL0 = 0x3C;
    
    timer_count++;
    led_flash_count++;
    
    // 每10ms执行一次传感器读取和处理
    if(timer_count >= 4) {
        timer_count = 0;
        
        // 读取传感器数据
        read_all_sensors();
        
        // 检查传感器异常
        check_sensor_error();
        
        // 自动跟踪处理
        if(mode == 1) {
            auto_tracking();
        }
    }
}

// 主程序
void main(void) {
    // 系统初始化
    system_init();
    
    // 主循环
    while(1) {
        // 按键扫描
        scan_keys();
        
        // 更新LED状态
        update_led_status();
        
        // 短暂延时
        delay_ms(10);
    }
}
