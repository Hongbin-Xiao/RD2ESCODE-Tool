#include <reg52.h>	         //调用单片机头文件
#define uchar unsigned char  //无符号字符型 宏定义	变量范围0~255
#define uint  unsigned int	 //无符号整型 宏定义	变量范围0~65535

#include <intrins.h>

uchar code smg_du[]={0xc0,0xf9,0xa4,0xb0,0x99,0x92,0x82,0x0f8,0x80,0x90,
0x88,0x83,0xc6,0xa1,0x86,0x8e};	 //断码	
										 //数码管位选定义
sbit smg_we1 = P2^0;	   
sbit smg_we2 = P2^2;
sbit smg_we3 = P2^4;
sbit smg_we4 = P2^6;
uchar dis_smg[8] = {0x14,0x77,0x4c,0x45,0x27,0x85,0x84};

sbit SCL=P1^2;		//SCL定义为P1口的第3位脚，连接ADC0832SCL脚
sbit DO=P1^3;		//DO定义为P1口的第4位脚，连接ADC0832DO脚
sbit CS=P1^0;		//CS定义为P1口的第4位脚，连接ADC0832CS脚

uchar shidu;     //湿度等级
uchar s_high = 70,s_low = 25;	//湿度报警参数

sbit dianji = P3^5;     //电机IO定义

/***********************1ms延时函数*****************************/
void delay_1ms(uint q)
{
	uint i,j;
	for(i=0;i<q;i++)
		for(j=0;j<120;j++);
}


/***********************数码位选函数*****************************/
void smg_we_switch(uchar i)
{
	switch(i)
	{
		case 0: smg_we1 = 1;  smg_we2 = 0; smg_we3 = 0;  smg_we4 = 0; break;
		case 1: smg_we1 = 0;  smg_we2 = 1; smg_we3 = 0;  smg_we4 = 0; break;
		case 2: smg_we1 = 0;  smg_we2 = 0; smg_we3 = 1;  smg_we4 = 0; break;
		case 3: smg_we1 = 0;  smg_we2 = 0; smg_we3 = 0;  smg_we4 = 1; break;
	}	
}

uchar flag_200ms ;
uchar key_can;		 //按键值的变量
uchar menu_1;        //菜单设计的变量

/***********************数码显示函数*****************************/
void display()
{
	static uchar i;   
	i++;
	if(i >= 4)
		i = 0;	
	P0 = 0xff;			 //消隐 
	smg_we_switch(i);		 //位选
	P0 = dis_smg[i];		 //段选	        
//	delay_1ms(1);
}

/***********读数模转换数据********************************************************/	
//请先了解ADC0832模数转换的串行协议，再来读本函数，主要是对应时序图来理解，本函数是模拟0832的串行协议进行的
						//  1  1  0 通道
						//  1  1  1 通道 
unsigned char ad0832read(bit SGL,bit ODD)
{
	unsigned char i=0,value=0,value1=0;		
		SCL=0;
		DO=1;
		CS=0;		//开始
		SCL=1;		//第一个上升沿	
		SCL=0;
		DO=SGL;
		SCL=1;  	//第二个上升沿
		SCL=0;
		DO=ODD;
		SCL=1;	   //第三个上升沿
		SCL=0;	   //第三个下降沿
		DO=1;
		for(i=0;i<8;i++)
		{
			SCL=1;
			SCL=0; //开始从第四个下降沿接收数据
			value=value<<1;
			if(DO)
				value++;						
		}
		for(i=0;i<8;i++)
		{			//接收校验数据
			value1>>=1;
			if(DO)
				value1+=0x80;
			SCL=1;
			SCL=0;
		}
		SCL=1;
		DO=1;
		CS=1;	
		if(value==value1)				//与校验数据比较，正确就返回数据，否则返回0	
			return value;
	return 0;
}



/********************独立按键程序*****************/
uchar key_can;	 //按键值

void key()	 //独立按键程序
{
	static uchar key_new;
	key_can = 20;                   //按键值还原
	P1 |= 0xf0;
	if((P1 & 0xf0) != 0xf0)		//按键按下
	{
		delay_1ms(1);	     	//按键消抖动
		if(((P1 & 0xf0) != 0xf0) && (key_new == 1))
		{						//确认是按键按下
			key_new = 0;
			switch(P1 & 0xf0)
			{
				case 0x70: key_can = 1; break;	   //得到k2键值
				case 0xb0: key_can = 2; break;	   //得到k3键值
				case 0xd0: key_can = 3; break;	   //得到k4键值
			}				
		}			
	}
	else 
		key_new = 1;	
}

/****************按键处理显示函数***************/
void key_with()
{
	if(menu_1 == 0)
	{
		if(key_can == 3)   //手动打开电机
			dianji = 0;     //打开电机
		if(key_can == 2)
			dianji = 1;     //关闭电机
		}

	if(key_can == 1)	 //设置键
	{
		menu_1 ++;
		if(menu_1 >= 3)
		{
			menu_1 = 0;

		}
	}
	if(menu_1 == 1)			//设置湿度上限
	{
		if(key_can == 2)
		{
			s_high ++ ;		//湿度上限值加1 
			if(s_high > 99)
				s_high = 99;
		}
		if(key_can == 3)
		{
			s_high -- ;		//湿度上限值减1 
			if(s_high <= s_low)
				s_high = s_low + 1 ;
		}
		dis_smg[0] = smg_du[s_high % 10];	           //取个位显示
		dis_smg[1] = smg_du[s_high / 10 % 10];  //取十位显示
		dis_smg[2] = 0xa1;	  
		dis_smg[3] = 0x8b;	 //H  0010 0110

	}	
	if(menu_1 == 2)			//设置湿度下限
	{
		if(key_can == 2)
		{
			s_low ++ ;	  //湿度下限值加1 
			if(s_low >= s_high)
				s_low = s_high - 1;
		}
		if(key_can == 3)
		{
			s_low --;	  //湿度下限值减1 
			if(s_low <= 1)
				s_low = 1;
		}
		dis_smg[0] = smg_du[s_low % 10];	           //取个位显示
		dis_smg[1] = smg_du[s_low / 10 % 10];  //取十位显示
		dis_smg[2] = 0xa1;	  
		dis_smg[3] = 0xc7;	 //L
	}	
}  

/****************电机控制函数***************/
void dianji_kongzi()
{
	static uchar value,value1;
	if(shidu <= s_low)
	{
		value ++;
		if(value >= 2)
		{
			value = 10;
			dianji = 1;       //打开电机
		}
	}
	else 
	  value = 0;
	if(shidu >= s_high)
	{
		value1 ++;
		if(value1 >= 2)
		{
			value1 = 10;
			dianji = 0;       //关机电机
		}
	}else 
		value1 = 0;
}

/***************主函数*****************/
void main()
{
	delay_1ms(100);
	P0 = P1 = P2 = P3 = 0xff;   //初始化IO口
	while(1)
	{
		key();					//独立按键程序
		if(key_can < 10)
		{
			key_with();			//按键按下要执行的程序
		}
		flag_200ms ++;
		if(flag_200ms >= 200)
		{		
			flag_200ms = 0;	  
			P0 = 0xff;			 //消隐 
			if(menu_1 == 0)
			{	   				
				shidu = ad0832read(1,0);	//读出湿度
				shidu = shidu * 99 / 255;
				dis_smg[0] = 0xff;	 //
				dis_smg[1] = smg_du[shidu % 10]; //取湿度的个位显示
				dis_smg[2] = smg_du[shidu / 10 % 10] ;	   //取湿度的十位显示
				dis_smg[3] = 0XFF;	// 
				dianji_kongzi();  //电机控制函数
			}
			
		} 
		display();  	//数码管显示函数
		delay_1ms(1);
	}
}

