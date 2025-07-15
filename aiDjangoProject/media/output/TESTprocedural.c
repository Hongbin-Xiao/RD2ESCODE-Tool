#include <reg52.h>
#define uchar unsigned char
#define uint unsigned int
#define Tol 15
#define PCF8591 0x90

sbit SCL = P1^1;
sbit SDA = P1^0;
sbit led_1 = P1^2;
sbit led_2 = P1^3;
sbit key_Up = P3^4;
sbit key_Down = P3^6;
sbit key_Left = P3^3;
sbit key_Right = P3^7;
sbit key_state = P3^5;

uchar code FirstSet_FWD[] = {0x01,0x03,0x02,0x06,0x04,0x0c,0x08,0x09};
uchar code FirstSet_REV[] = {0x09,0x08,0x0c,0x04,0x06,0x02,0x03,0x01};
uchar code Secondset_FWD[] = {0x10,0x30,0x20,0x60,0x40,0xc0,0x80,0x90};
uchar code Secondset_REV[] = {0x90,0x80,0xc0,0x40,0x60,0x20,0x30,0x10};

uint angle_X = 800, angle_Y = 800;
bit DIR_X, DIR_Y;
uchar loop, AD_Up, AD_Down, AD_Left, AD_Right, ms, blink_ms;
bit Up_CB, Down_CB, Left_CB, Right_CB, SYS_mode, SYS_ERROR;

void pcf_delay() {
    ;
}

void i2c_start() {
    SDA = 1; pcf_delay();
    SCL = 1; pcf_delay();
    SDA = 0; pcf_delay();
}

void i2c_stop() {
    SDA = 0; pcf_delay();
    SCL = 1; pcf_delay();
    SDA = 1; pcf_delay();
}

void i2c_resp() {
    uchar i = 0;
    SCL = 1; pcf_delay();
    while ((SDA == 1) && (i < 250)) i++;
    SCL = 0; pcf_delay();
}

void i2c_init() {
    SDA = 1; pcf_delay();
    SCL = 1; pcf_delay();
}

uchar i2c_readbyte() {
    uchar i, k = 0;
    SCL = 0; pcf_delay();
    SDA = 1; pcf_delay();
    for (i = 0; i < 8; i++) {
        SCL = 1; pcf_delay();
        k = (k << 1) | SDA;
        SCL = 0; pcf_delay();
    }
    return k;
}

void i2c_writebyte(uchar date) {
    uchar i, temp;
    temp = date;
    for (i = 0; i < 8; i++) {
        temp = temp << 1;
        SCL = 0; pcf_delay();
        SDA = CY; pcf_delay();
        SCL = 1; pcf_delay();
    }
    SCL = 0; pcf_delay();
    SDA = 1; pcf_delay();
}

uchar read_sensor(uchar channel) {
    uchar d;
    i2c_start();
    i2c_writebyte(PCF8591); i2c_resp();
    i2c_writebyte(channel); i2c_resp();
    i2c_start();
    i2c_writebyte(PCF8591 + 1); i2c_resp();
    d = i2c_readbyte();
    i2c_stop();
    return d;
}

uchar write_dac(uchar light) {
    i2c_start();
    i2c_writebyte(PCF8591); i2c_resp();
    i2c_writebyte(0x40); i2c_resp();
    i2c_writebyte(light); i2c_resp();
    i2c_stop();
    return 1;
}

void wait(uint t) {
    while (t--);
}

void check_key() {
    if (!key_state) {
        wait(1000);
        if (!key_state) {
            while (!key_state)
                Down_CB = Up_CB = Right_CB = Left_CB = 0;
            SYS_mode = !SYS_mode;
            angle_X = angle_Y = 800;
            DIR_X = DIR_Y = 0;
        }
    }

    if (!SYS_mode) {
        if (!key_Up) {
            Up_CB = 1; Down_CB = 0;
        } else if (!key_Down) {
            Up_CB = 0; Down_CB = 1;
        } else {
            Down_CB = 0; Up_CB = 0;
        }
        if (!key_Left) {
            Left_CB = 1; Right_CB = 0;
        } else if (!key_Right) {
            Left_CB = 0; Right_CB = 1;
        } else {
            Right_CB = 0; Left_CB = 0;
        }
    }
}

void auto_control() {
    if (SYS_mode && SYS_ERROR == 0) {
        if (AD_Up > AD_Down) {
            Up_CB = 0;
            if (AD_Up - AD_Down >= Tol) Down_CB = 1;
            else if (AD_Up - AD_Down <= 4) Down_CB = 0;
        } else {
            Down_CB = 0;
            if (AD_Down - AD_Up >= Tol) Up_CB = 1;
            else if (AD_Down - AD_Up <= 4) Up_CB = 0;
        }
        if (AD_Left > AD_Right) {
            Right_CB = 0;
            if (AD_Left - AD_Right >= Tol) Left_CB = 1;
            else if (AD_Left - AD_Right <= 7) Left_CB = 0;
        } else {
            Left_CB = 0;
            if (AD_Right - AD_Left >= Tol) Right_CB = 1;
            else if (AD_Right - AD_Left <= 7) Right_CB = 0;
        }
    } else if (SYS_mode && SYS_ERROR) {
        Right_CB = Left_CB = Up_CB = Down_CB = 0;
    }
}

void check_sys_err() {
    if (AD_Down == 255 || AD_Down == 0 || AD_Up == 255 || AD_Up == 0 ||
        AD_Right == 255 || AD_Right == 0 || AD_Left == 255 || AD_Left == 0)
        SYS_ERROR = 1;
    else
        SYS_ERROR = 0;
}

void update_led() {
    if (SYS_ERROR == 0) {
        if (!SYS_mode) {
            led_1 = 0; led_2 = 1;
        } else {
            led_1 = 1; led_2 = 0;
        }
    }
}

void main(void) {
    TMOD = 0x01;
    TH0 = 0xf6;
    TL0 = 0x3b;
    EA = 1;
    ET0 = 1;
    TR0 = 1;
    i2c_init();

    while (1) {
        check_key();
        AD_Down = read_sensor(0x00);
        AD_Up = read_sensor(0x01);
        AD_Right = read_sensor(0x02);
        AD_Left = read_sensor(0x03);
        check_sys_err();
        auto_control();
        update_led();
    }
}

void timer0_proc() interrupt 1 {
    TH0 = 0xf6; TL0 = 0x3b;
    if (Up_CB) {
        P2 = P2 & 0xf0 | FirstSet_FWD[loop];
    } else if (Down_CB) {
        P2 = P2 & 0xf0 | FirstSet_REV[loop];
    } else {
        P2 = P2 & 0xf0;
    }

    if (Left_CB) {
        P2 = P2 & 0x0f | Secondset_FWD[loop];
    } else if (Right_CB) {
        P2 = P2 & 0x0f | Secondset_REV[loop];
    } else {
        P2 = P2 & 0x0f;
    }

    loop = (loop + 1) % 8;

    if (SYS_ERROR == 1) {
        blink_ms++;
        if (blink_ms > 39) {
            blink_ms = 0;
            led_1 = !led_1;
            led_2 = led_1;
        }
    }
}