#include <reg52.h>
#include <intrins.h>

#define uchar unsigned char	// �Ժ�unsigned char�Ϳ�����uchar����
#define uint  unsigned int	// �Ժ�unsigned int �Ϳ�����uint ����

sfr ISP_DATA  = 0xe2;		// ���ݼĴ���
sfr ISP_ADDRH = 0xe3;		// ��ַ�Ĵ����߰�λ
sfr ISP_ADDRL = 0xe4;		// ��ַ�Ĵ����Ͱ�λ
sfr ISP_CMD   = 0xe5;		// ����Ĵ���
sfr ISP_TRIG  = 0xe6;		// ������Ĵ���
sfr ISP_CONTR = 0xe7;		// ����Ĵ���

sbit LcdRs_P    = P2^7;       // 1602Һ����RS�ܽ�       
sbit LcdRw_P    = P2^6;       // 1602Һ����RW�ܽ� 
sbit LcdEn_P    = P2^5;       // 1602Һ����EN�ܽ�
sbit RST_P      = P1^3;				// ʱ��оƬDS1302��RST�ܽ�
sbit SDA_P      = P1^2;				// ʱ��оƬDS1302��SDA�ܽ�
sbit SCK_P      = P1^1;				// ʱ��оƬDS1302��SCK�ܽ�
sbit KeySet_P   = P3^2;				// ����ʱ�䰴��
sbit KeyClock_P = P3^3;				// �������Ӱ���
sbit KeyDown_P  = P3^4;				// ������
sbit KeyUp_P    = P3^5;				// �Ӱ���
sbit Buzzer_P   = P2^0;				// ������


uchar TimeBuff[7]={16,8,5,6,18,30,50};				// ʱ�����飬Ĭ��2016��8��5�գ������壬16:30:50
// TimeBuff[0] ������ݣ���Χ00-99
// TimeBuff[1] �����·ݣ���Χ1-12
// TimeBuff[2] �������ڣ���Χ1-31
// TimeBuff[3] �������ڣ���Χ1-7��1�������죬2������һ... ...
// TimeBuff[4] ����Сʱ����Χ00-23
// TimeBuff[5] ������ӣ���Χ00-59
// TimeBuff[6] �������ӣ���Χ00-59


uchar Clock_Hour;					// ���ӵ�Сʱ
uchar Clock_Minute;				// ���ӵķ���
uchar Clock_Swt;					// ���ӵĿ���
uchar Buzzer_Flag=0;			// ������������־



/*********************************************************/
// ��Ƭ���ڲ�EEPROM��ʹ��
/*********************************************************/
void ISP_Disable()
{
	ISP_CONTR = 0;
	ISP_ADDRH = 0;
	ISP_ADDRL = 0;
}


/*********************************************************/
// �ӵ�Ƭ���ڲ�EEPROM��һ���ֽڣ���0x2000��ַ��ʼ
/*********************************************************/
unsigned char EEPROM_Read(unsigned int add)
{
	ISP_DATA  = 0x00;
	ISP_CONTR = 0x83;
	ISP_CMD   = 0x01;
	ISP_ADDRH = (unsigned char)(add>>8);
	ISP_ADDRL = (unsigned char)(add&0xff);
	// ��STC89C51ϵ����˵��ÿ��Ҫд��0x46����д��0xB9,ISP/IAP�Ż���Ч
	ISP_TRIG  = 0x46;	   
	ISP_TRIG  = 0xB9;
	_nop_();
	ISP_Disable();
	return (ISP_DATA);
}


/*********************************************************/
// ����Ƭ���ڲ�EEPROMдһ���ֽڣ���0x2000��ַ��ʼ
/*********************************************************/
void EEPROM_Write(unsigned int add,unsigned char ch)
{
	ISP_CONTR = 0x83;
	ISP_CMD   = 0x02;
	ISP_ADDRH = (unsigned char)(add>>8);
	ISP_ADDRL = (unsigned char)(add&0xff);
	ISP_DATA  = ch;
	ISP_TRIG  = 0x46;
	ISP_TRIG  = 0xB9;
	_nop_();
	ISP_Disable();
}


/*********************************************************/
// ������Ƭ���ڲ�EEPROM��һ������
// д8�����������һ���ĵ�ַ���������������д��ǰҪ�Ȳ���
/*********************************************************/
void Sector_Erase(unsigned int add)	  
{
	ISP_CONTR = 0x83;
	ISP_CMD   = 0x03;
	ISP_ADDRH = (unsigned char)(add>>8);
	ISP_ADDRL = (unsigned char)(add&0xff);
	ISP_TRIG  = 0x46;
	ISP_TRIG  = 0xB9;
	_nop_();
	ISP_Disable();
}


/*********************************************************/
// ���뼶����ʱ������time��Ҫ��ʱ�ĺ�����
/*********************************************************/
void DelayMs(uint time)
{
	uint i,j;
	for(i=time;i>0;i--)
		for(j=112;j>0;j--);
}


/*********************************************************/
// 1602Һ��д�������cmd����Ҫд�������
/*********************************************************/
void LcdWriteCmd(uchar cmd)
{ 
	LcdRs_P = 0;
	LcdRw_P = 0;
	LcdEn_P = 0;
	P0=cmd;
	DelayMs(2);
	LcdEn_P = 1;    
	DelayMs(2);
	LcdEn_P = 0;	
}


/*********************************************************/
// 1602Һ��д���ݺ�����dat����Ҫд�������
/*********************************************************/
void LcdWriteData(uchar dat)
{
	LcdRs_P = 1; 
	LcdRw_P = 0;
	LcdEn_P = 0;
	P0=dat;
	DelayMs(2);
	LcdEn_P = 1;    
	DelayMs(2);
	LcdEn_P = 0;
}


/*********************************************************/
// 1602Һ����ʼ������
/*********************************************************/
void LcdInit()
{
	LcdWriteCmd(0x38);        // 16*2��ʾ��5*7����8λ���ݿ�
	LcdWriteCmd(0x0C);        // ����ʾ������ʾ���
	LcdWriteCmd(0x06);        // ��ַ��1����д�����ݺ�������
	LcdWriteCmd(0x01);        // ����
}


/*********************************************************/
// Һ����궨λ����
/*********************************************************/
void LcdGotoXY(uchar line,uchar column)
{
	// ��һ��
	if(line==0)        
		LcdWriteCmd(0x80+column); 
	// �ڶ���
	if(line==1)        
		LcdWriteCmd(0x80+0x40+column); 
}


/*********************************************************/
// Һ������ַ�������
/*********************************************************/
void LcdPrintStr(uchar *str)
{
	while(*str!='\0')
			LcdWriteData(*str++);
}


/*********************************************************/
// Һ����ʾ���ݵĳ�ʼ��
/*********************************************************/
void LcdShowInit()
{
	LcdGotoXY(0,0);
	LcdPrintStr("20  -  -        ");
	LcdGotoXY(1,0);
	LcdPrintStr("      :  :      ");
}



/*********************************************************/
// Һ���������
/*********************************************************/
void LcdPrintNum(uchar num)
{
	LcdWriteData(num/10+48);		// ʮλ
	LcdWriteData(num%10+48); 		// ��λ
}


/*********************************************************/
// Һ����ʾ����
/*********************************************************/
void LcdPrintWeek(uchar week)
{
	switch(week)
	{
		case 1: LcdPrintStr(" Sun");	break;
		case 2: LcdPrintStr(" Mon");	break;
		case 3: LcdPrintStr("Tues");	break;
		case 4: LcdPrintStr(" Wed");	break;
		case 5: LcdPrintStr("Thur");	break;
		case 6: LcdPrintStr(" Fri");	break;
		case 7: LcdPrintStr(" Sat");	break;
		default:											break;
	}
}


/*********************************************************/
// ˢ��ʱ����ʾ
/*********************************************************/
void FlashTime()
{
	LcdGotoXY(0,2);										// ���
	LcdPrintNum(TimeBuff[0]);
	LcdGotoXY(0,5);										// �·�
	LcdPrintNum(TimeBuff[1]);
	LcdGotoXY(0,8);										// ����
	LcdPrintNum(TimeBuff[2]);
	LcdGotoXY(1,4);										// Сʱ
	LcdPrintNum(TimeBuff[4]);
	LcdGotoXY(1,7);										// ����
	LcdPrintNum(TimeBuff[5]);
	LcdGotoXY(1,10);									// ����
	LcdPrintNum(TimeBuff[6]);
	LcdGotoXY(0,12);									// ����	
	LcdPrintWeek(TimeBuff[3]);
}




/*********************************************************/
// ��ʼ��DS1302
/*********************************************************/
void DS1302_Init(void)
{
	RST_P=0;			// RST���õ�
	SCK_P=0;			// SCK���õ�
	SDA_P=0;			// SDA���õ�				
}



/*********************************************************/
// ��DS1302����һ�ֽ�����
/*********************************************************/
uchar DS1302_Read_Byte(uchar addr) 
{
	uchar i;
	uchar temp;
	
	RST_P=1;								
	
	/* д��Ŀ���ַ��addr*/
	for(i=0;i<8;i++) 
	{     
		if(addr&0x01) 
			SDA_P=1;
		else 
			SDA_P=0;
		
		SCK_P=1;
		_nop_();
		SCK_P=0;
		_nop_();
		
		addr=addr>> 1;
	}
	
	/* �����õ�ַ������ */
	for(i=0;i<8;i++) 
	{
		temp=temp>>1;
		
		if(SDA_P) 
			temp|= 0x80;
		else 
			temp&=0x7F;
		
		SCK_P=1;
		_nop_();
		SCK_P=0;
		_nop_();
	}
	
	RST_P=0;
	
	return temp;
}



/*********************************************************/
// ��DS1302д��һ�ֽ�����
/*********************************************************/
void DS1302_Write_Byte(uchar addr, uchar dat)
{
	uchar i;
	
	RST_P = 1;
	
	/* д��Ŀ���ַ��addr*/
	for(i=0;i<8;i++) 
	{ 
		if(addr&0x01) 
			SDA_P=1;
		else 
			SDA_P=0;

		SCK_P=1;
		_nop_();
		SCK_P=0;
		_nop_();
		
		addr=addr>>1;
	}
	
	/* д�����ݣ�dat*/
	for(i=0;i<8;i++) 
	{
		if(dat&0x01) 
			SDA_P=1;
		else 
			SDA_P=0;
	
		SCK_P=1;
		_nop_();
		SCK_P=0;
		_nop_();
		
		dat=dat>>1;
	}
	
	RST_P=0;					
}



/*********************************************************/
// ��DS1302д��ʱ������
/*********************************************************/
void DS1302_Write_Time() 
{
  uchar i;
	uchar temp1;
	uchar temp2;
	
	for(i=0;i<7;i++)			// ʮ����תBCD��
	{
		temp1=(TimeBuff[i]/10)<<4;
		temp2=TimeBuff[i]%10;
		TimeBuff[i]=temp1+temp2;
	}
	
	DS1302_Write_Byte(0x8E,0x00);								// �ر�д���� 
	DS1302_Write_Byte(0x80,0x80);								// ��ͣʱ�� 
	DS1302_Write_Byte(0x8C,TimeBuff[0]);				// �� 
	DS1302_Write_Byte(0x88,TimeBuff[1]);				// �� 
	DS1302_Write_Byte(0x86,TimeBuff[2]);				// �� 
	DS1302_Write_Byte(0x8A,TimeBuff[3]);				// ����
	DS1302_Write_Byte(0x84,TimeBuff[4]);				// ʱ 
	DS1302_Write_Byte(0x82,TimeBuff[5]);				// ��
	DS1302_Write_Byte(0x80,TimeBuff[6]);				// ��
	DS1302_Write_Byte(0x80,TimeBuff[6]&0x7F);		// ����ʱ��
	DS1302_Write_Byte(0x8E,0x80);								// ��д����  
}




/*********************************************************/
// ��DS1302����ʱ������
/*********************************************************/
void DS1302_Read_Time()  
{ 
	uchar i;

	TimeBuff[0]=DS1302_Read_Byte(0x8D);						// �� 
	TimeBuff[1]=DS1302_Read_Byte(0x89);						// �� 
	TimeBuff[2]=DS1302_Read_Byte(0x87);						// �� 
	TimeBuff[3]=DS1302_Read_Byte(0x8B);						// ����
	TimeBuff[4]=DS1302_Read_Byte(0x85);						// ʱ 
	TimeBuff[5]=DS1302_Read_Byte(0x83);						// �� 
	TimeBuff[6]=(DS1302_Read_Byte(0x81))&0x7F;		// �� 

	for(i=0;i<7;i++)		// BCDתʮ����
	{           
		TimeBuff[i]=(TimeBuff[i]/16)*10+TimeBuff[i]%16;
	}
}




/*********************************************************/
// ����ɨ��(����ʱ��)
/*********************************************************/
void KeyScanf1()
{
	if(KeySet_P==0)
	{
		LcdWriteCmd(0x0f);			// ���������˸
		LcdGotoXY(0,3);					// ��λ��굽�����˸
		DelayMs(10);						// ��ʱ�ȴ��������������µĶ���
		while(!KeySet_P);				// �ȴ������ͷ�
		DelayMs(10);						// ��ʱ�ȴ������������ɿ��Ķ���
		
		/* ������� */
		while(1)
		{
			if(KeyDown_P==0)							// �������������ȥ
			{
				if(TimeBuff[0]>0)						// �ж�����Ƿ����0		
					TimeBuff[0]--;						// �ǵĻ��ͼ�ȥ1
				LcdGotoXY(0,2);							// ��궨λ����ݵ�λ��
				LcdPrintNum(TimeBuff[0]);		// ˢ����ʾ�ı������
				LcdGotoXY(0,3);							// ��λ��굽�����˸
				DelayMs(300);								// ��ʱ0.3������
			}
			
			if(KeyUp_P==0)								// ����Ӱ�������ȥ
			{
				if(TimeBuff[0]<99)					// �ж�����Ƿ�С��99
					TimeBuff[0]++;						// �ǵĻ��ͼ���1
				LcdGotoXY(0,2);							// ��궨λ����ݵ�λ��
				LcdPrintNum(TimeBuff[0]);		// ˢ����ʾ�ı������
				LcdGotoXY(0,3);							// ��λ��굽�����˸
				DelayMs(300);								// ��ʱ0.3������
			}
			
			if(KeySet_P==0)
			{
				break;
			}
		}
		
		LcdGotoXY(0,6);					// ��λ��굽�·���˸
		DelayMs(10);						// ��ʱ�ȴ��������������µĶ���
		while(!KeySet_P);				// �ȴ������ͷ�
		DelayMs(10);						// ��ʱ�ȴ������������ɿ��Ķ���
			
		/* �����·� */
		while(1)
		{
			if(KeyDown_P==0)							// �������������ȥ
			{
				if(TimeBuff[1]>1)						// �ж��·��Ƿ����1		
					TimeBuff[1]--;						// �ǵĻ��ͼ�ȥ1
				LcdGotoXY(0,5);							// ��궨λ���·ݵ�λ��
				LcdPrintNum(TimeBuff[1]);		// ˢ����ʾ�ı����·�
				LcdGotoXY(0,6);							// ��λ��굽�·���˸
				DelayMs(300);								// ��ʱ0.3������
			}
			
			if(KeyUp_P==0)								// ����Ӱ�������ȥ
			{
				if(TimeBuff[1]<12)					// �ж��·��Ƿ�С��12
					TimeBuff[1]++;						// �ǵĻ��ͼ���1
				LcdGotoXY(0,5);							// ��궨λ���·ݵ�λ��
				LcdPrintNum(TimeBuff[1]);		// ˢ����ʾ�ı����·�
				LcdGotoXY(0,6);							// ��λ��굽�·���˸
				DelayMs(300);								// ��ʱ0.3������
			}
			
			if(KeySet_P==0)
			{
				break;
			}
		}
		
		LcdGotoXY(0,9);					// ��λ��굽������˸
		DelayMs(10);						// ��ʱ�ȴ��������������µĶ���
		while(!KeySet_P);				// �ȴ������ͷ�
		DelayMs(10);						// ��ʱ�ȴ������������ɿ��Ķ���
		
		/* �������� */
		while(1)
		{
			if(KeyDown_P==0)							// �������������ȥ
			{
				if(TimeBuff[2]>1)						// �ж������Ƿ����1		
					TimeBuff[2]--;						// �ǵĻ��ͼ�ȥ1
				LcdGotoXY(0,8);							// ��궨λ�����ڵ�λ��
				LcdPrintNum(TimeBuff[2]);		// ˢ����ʾ�ı�������
				LcdGotoXY(0,9);							// ��λ��굽������˸
				DelayMs(300);								// ��ʱ0.3������
			}
			
			if(KeyUp_P==0)								// ����Ӱ�������ȥ
			{
				if(TimeBuff[2]<31)					// �ж������Ƿ�С��31
					TimeBuff[2]++;						// �ǵĻ��ͼ���1
				LcdGotoXY(0,8);							// ��궨λ�����ڵ�λ��
				LcdPrintNum(TimeBuff[2]);		// ˢ����ʾ�ı�������
				LcdGotoXY(0,9);							// ��λ��굽������˸
				DelayMs(300);								// ��ʱ0.3������
			}
			
			if(KeySet_P==0)
			{
				break;
			}
		}
		
		LcdGotoXY(0,15);				// ��λ��굽������˸
		DelayMs(10);						// ��ʱ�ȴ��������������µĶ���
		while(!KeySet_P);				// �ȴ������ͷ�
		DelayMs(10);						// ��ʱ�ȴ������������ɿ��Ķ���
		
		/* �������� */
		while(1)
		{
			if(KeyDown_P==0)							// �������������ȥ
			{
				if(TimeBuff[3]>1)						// �ж������Ƿ����1		
					TimeBuff[3]--;						// �ǵĻ��ͼ�ȥ1
				LcdGotoXY(0,12);						// ��궨λ�����ڵ�λ��
				LcdPrintWeek(TimeBuff[3]);	// ˢ����ʾ�ı�������
				LcdGotoXY(0,15);						// ��λ��굽������˸
				DelayMs(300);								// ��ʱ0.3������
			}
			
			if(KeyUp_P==0)								// ����Ӱ�������ȥ
			{
				if(TimeBuff[3]<7)						// �ж������Ƿ�С��6
					TimeBuff[3]++;						// �ǵĻ��ͼ���1
				LcdGotoXY(0,12);						// ��궨λ�����ڵ�λ��
				LcdPrintWeek(TimeBuff[3]);	// ˢ����ʾ�ı�������
				LcdGotoXY(0,15);						// ��λ��굽������˸
				DelayMs(300);								// ��ʱ0.3������
			}
			
			if(KeySet_P==0)
			{
				break;
			}
		}
		
		LcdGotoXY(1,5);					// ��λ��굽Сʱ��˸
		DelayMs(10);						// ��ʱ�ȴ��������������µĶ���
		while(!KeySet_P);				// �ȴ������ͷ�
		DelayMs(10);						// ��ʱ�ȴ������������ɿ��Ķ���
		
		/* ����Сʱ */
		while(1)
		{
			if(KeyDown_P==0)							// �������������ȥ
			{
				if(TimeBuff[4]>0)						// �ж�Сʱ�Ƿ����0
					TimeBuff[4]--;						// �ǵĻ��ͼ�ȥ1
				LcdGotoXY(1,4);							// ��궨λ��Сʱ��λ��
				LcdPrintNum(TimeBuff[4]);		// ˢ����ʾ�ı���Сʱ
				LcdGotoXY(1,5);							// ��λ��굽Сʱ��˸
				DelayMs(300);								// ��ʱ0.3������
			}
			
			if(KeyUp_P==0)								// ����Ӱ�������ȥ
			{
				if(TimeBuff[4]<23)					// �ж�Сʱ�Ƿ�С��23
					TimeBuff[4]++;						// �ǵĻ��ͼ���1
				LcdGotoXY(1,4);							// ��궨λ��Сʱ��λ��
				LcdPrintNum(TimeBuff[4]);		// ˢ����ʾ�ı���Сʱ
				LcdGotoXY(1,5);							// ��λ��굽Сʱ��˸
				DelayMs(300);								// ��ʱ0.3������
			}
			
			if(KeySet_P==0)
			{
				break;
			}
		}
		
		LcdGotoXY(1,8);					// ��λ��굽������˸
		DelayMs(10);						// ��ʱ�ȴ��������������µĶ���
		while(!KeySet_P);				// �ȴ������ͷ�
		DelayMs(10);						// ��ʱ�ȴ������������ɿ��Ķ���
		
		/* �������� */
		while(1)
		{
			if(KeyDown_P==0)							// �������������ȥ
			{
				if(TimeBuff[5]>0)						// �жϷ����Ƿ����0
					TimeBuff[5]--;						// �ǵĻ��ͼ�ȥ1
				LcdGotoXY(1,7);							// ��궨λ�����ӵ�λ��
				LcdPrintNum(TimeBuff[5]);		// ˢ����ʾ�ı��ķ���
				LcdGotoXY(1,8);							// ��λ��굽������˸
				DelayMs(300);								// ��ʱ0.3������
			}
			
			if(KeyUp_P==0)								// ����Ӱ�������ȥ
			{
				if(TimeBuff[5]<59)					// �жϷ����Ƿ�С��59
					TimeBuff[5]++;						// �ǵĻ��ͼ���1
				LcdGotoXY(1,7);							// ��궨λ�����ӵ�λ��
				LcdPrintNum(TimeBuff[5]);		// ˢ����ʾ�ı��ķ���
				LcdGotoXY(1,8);							// ��λ��굽������˸
				DelayMs(300);								// ��ʱ0.3������
			}
			
			if(KeySet_P==0)
			{
				break;
			}
		}
		
		LcdGotoXY(1,11);				// ��λ��굽������˸
		DelayMs(10);						// ��ʱ�ȴ��������������µĶ���
		while(!KeySet_P);				// �ȴ������ͷ�
		DelayMs(10);						// ��ʱ�ȴ������������ɿ��Ķ���
		
		/* �������� */
		while(1)
		{
			if(KeyDown_P==0)							// �������������ȥ
			{
				if(TimeBuff[6]>0)						// �ж������Ƿ����0
					TimeBuff[6]--;						// �ǵĻ��ͼ�ȥ1
				LcdGotoXY(1,10);						// ��궨λ�����ӵ�λ��
				LcdPrintNum(TimeBuff[6]);		// ˢ����ʾ�ı�������
				LcdGotoXY(1,11);						// ��λ��굽������˸
				DelayMs(300);								// ��ʱ0.3������
			}
			
			if(KeyUp_P==0)								// ����Ӱ�������ȥ
			{
				if(TimeBuff[6]<59)					// �ж������Ƿ�С��59
					TimeBuff[6]++;						// �ǵĻ��ͼ���1
				LcdGotoXY(1,10);						// ��궨λ�����ӵ�λ��
				LcdPrintNum(TimeBuff[6]);		// ˢ����ʾ�ı�������
				LcdGotoXY(1,11);						// ��λ��굽������˸
				DelayMs(300);								// ��ʱ0.3������
			}
			
			if(KeySet_P==0)
			{
				break;
			}
		}
		
		/* �˳�ǰ������ */
		LcdWriteCmd(0x0C);			// �رչ����˸
		DS1302_Write_Time();		// �������õ�ʱ��ֵ����DS1302оƬ
		DelayMs(10);						// ��ʱ�ȴ��������������µĶ���
		while(!KeySet_P);				// �ȴ������ͷ�
		DelayMs(10);						// ��ʱ�ȴ������������ɿ��Ķ���
	}
}



/*********************************************************/
// ����ɨ��(��������)
/*********************************************************/
void KeyScanf2()
{
	if(KeyClock_P==0)
	{
		LcdGotoXY(0,0);										// Һ����ʾΪ�������õĽ���
		LcdPrintStr("Alarm Clock Set ");
		LcdGotoXY(1,0);				
		LcdPrintStr("     :          ");
		LcdGotoXY(1,3);										// ��ʾ���ӵ�Сʱ
		LcdPrintNum(Clock_Hour);
		LcdGotoXY(1,6);										// ��ʾ���ӵķ���
		LcdPrintNum(Clock_Minute);
		LcdGotoXY(1,10);									// ��ʾ����״̬
		if(Clock_Swt==0)
		{
			LcdPrintStr("OFF");
		}
		else
		{
			LcdPrintStr(" ON");
		}
		LcdGotoXY(1,4);										// ��궨λ
		LcdWriteCmd(0x0f);								// �����˸
		DelayMs(10);											// ��ʱ�ȴ��������������µĶ���
		while(!KeyClock_P);								// �ȴ������ͷ�
		DelayMs(10);											// ��ʱ�ȴ������������ɿ��Ķ���
		
		/* ��������Сʱ */
		while(1)
		{
			if(KeyDown_P==0)							// �������������ȥ
			{
				if(Clock_Hour>0)						// �ж�����Сʱ�Ƿ����0
					Clock_Hour--;							// �ǵĻ��ͼ�ȥ1
				LcdGotoXY(1,3);							// ��궨λ������Сʱ��λ��
				LcdPrintNum(Clock_Hour);		// ˢ����ʾ�ı�������Сʱ
				LcdGotoXY(1,4);							// ��λ��굽����Сʱ��˸
				DelayMs(300);								// ��ʱ0.3������
			}
			
			if(KeyUp_P==0)								// ����Ӱ�������ȥ
			{
				if(Clock_Hour<23)						// �ж�����Сʱ�Ƿ�С��23
					Clock_Hour++;							// �ǵĻ��ͼ���1
				LcdGotoXY(1,3);							// ��궨λ������Сʱ��λ��
				LcdPrintNum(Clock_Hour);		// ˢ����ʾ�ı�������Сʱ
				LcdGotoXY(1,4);							// ��λ��굽����Сʱ��˸
				DelayMs(300);								// ��ʱ0.3������
			}
			
			if(KeyClock_P==0)
			{
				break;
			}
		}
		
		LcdGotoXY(1,7);					// ��λ��굽���ӷ��ӵ���˸
		DelayMs(10);						// ��ʱ�ȴ��������������µĶ���
		while(!KeyClock_P);			// �ȴ������ͷ�
		DelayMs(10);						// ��ʱ�ȴ������������ɿ��Ķ���
		
		/* �������� */
		while(1)
		{
			if(KeyDown_P==0)							// �������������ȥ
			{
				if(Clock_Minute>0)					// �ж����ӷ����Ƿ����0
					Clock_Minute--;						// �ǵĻ��ͼ�ȥ1
				LcdGotoXY(1,6);							// ��궨λ�����ӷ��ӵ�λ��
				LcdPrintNum(Clock_Minute);	// ˢ����ʾ�ı������ӷ���
				LcdGotoXY(1,7);							// ��λ��굽���ӷ�����˸
				DelayMs(300);								// ��ʱ0.3������
			}
			
			if(KeyUp_P==0)								// ����Ӱ�������ȥ
			{
				if(Clock_Minute<59)					// �ж����ӷ����Ƿ�С��59
					Clock_Minute++;						// �ǵĻ��ͼ���1
				LcdGotoXY(1,6);							// ��궨λ�����ӷ��ӵ�λ��
				LcdPrintNum(Clock_Minute);	// ˢ����ʾ�ı������ӷ���
				LcdGotoXY(1,7);							// ��λ��굽���ӷ�����˸
				DelayMs(300);								// ��ʱ0.3������
			}
			
			if(KeyClock_P==0)
			{
				break;
			}
		}
		
		LcdGotoXY(1,12);				// ��λ��굽���ӿ��ص�λ����˸
		DelayMs(10);						// ��ʱ�ȴ��������������µĶ���
		while(!KeyClock_P);			// �ȴ������ͷ�
		DelayMs(10);						// ��ʱ�ȴ������������ɿ��Ķ���
		
		/* ���ӿ��� */
		while(1)
		{
			if(KeyDown_P==0)							// �������������ȥ
			{
				if(Clock_Swt==1)						// �ж������Ƿ���
					Clock_Swt=0;							// �ر�����
				LcdGotoXY(1,10);						// ��궨λ�����ӿ��ص�λ��
				LcdPrintStr("OFF");					// Һ����ʾ��OFF��
				LcdGotoXY(1,12);						// ��λ��굽���ӿ��ص�λ����˸
				DelayMs(300);								// ��ʱ0.3������
			}
			
			if(KeyUp_P==0)									// ����Ӱ�������ȥ
			{
				if(Clock_Swt==0)						// �ж������Ƿ�ر�
					Clock_Swt=1;							// ��������
				LcdGotoXY(1,10);						// ��궨λ�����ӿ��ص�λ��
				LcdPrintStr(" ON");					// Һ����ʾ�� ON��
				LcdGotoXY(1,12);						// ��λ��굽���ӿ��ص�λ����˸
				DelayMs(300);								// ��ʱ0.3������
			}
			
			if(KeyClock_P==0)
			{
				break;
			}
		}
		
		/* �˳�ǰ������ */
		LcdWriteCmd(0x0C);			// �رչ����˸
		LcdShowInit();					// Һ����ʾ���ݻָ�Ϊ�������
		DelayMs(10);						// ��ʱ�ȴ��������������µĶ���
		while(!KeyClock_P);			// �ȴ������ͷ�
		DelayMs(10);						// ��ʱ�ȴ������������ɿ��Ķ���
		Sector_Erase(0x2000);
		EEPROM_Write(0x2000,Clock_Hour);			// ��0x2000�����ַд�����ӵ�Сʱ 
		EEPROM_Write(0x2001,Clock_Minute);		// ��0x2001�����ַд�����ӵķ���
		EEPROM_Write(0x2002,Clock_Swt);				// ��0x2002�����ַд�����ӵĿ���
	}
}



/*********************************************************/
// �����ж�
/*********************************************************/
void ClockJudge()
{
	if(Clock_Swt==1)			// �ж����ӵĿ����Ƿ���
	{
		if((Clock_Hour==TimeBuff[4])&&(Clock_Minute==TimeBuff[5]))		// ��ǰСʱ�ͷ��ӣ������ӵ�Сʱ�ͷ����Ƿ�һ��
		{
			if(TimeBuff[6]==0)								// �����Ƿ����0
			{
				Buzzer_Flag=1;									// ����������������־
			}
		}
	}
	
	if(TimeBuff[6]==59)										// �����ǰ����Ϊ59��
	{
		Buzzer_Flag=0;											// �رշ�����������־
	}
	
	if((KeyDown_P==0)||(KeyUp_P==0))			// ����Ӱ����������������
	{
		Buzzer_Flag=0;											// �رշ�����������־
	}
	
	if(Buzzer_Flag==1)										// ���������������־Ϊ����
	{
		Buzzer_P=0;													// ����������
		DelayMs(100);												// ��ʱ0.1��
		Buzzer_P=1;													// �رշ�����
		DelayMs(100);												// ��ʱ0.1��
	}
}


/*********************************************************/
// ������
/*********************************************************/
void main()
{
	LcdInit();			// ִ��Һ����ʼ��	
	DS1302_Init();	// ʱ��оƬ�ĳ�ʼ��
	LcdShowInit();	// Һ����ʾ���ݵĳ�ʼ��

	if(DS1302_Read_Byte(0x81)>=128)			// �ж�ʱ��оƬ�Ƿ���������
	{
		DS1302_Write_Time();							// ���û�У����ʼ��һ��ʱ��
	}
	

	Clock_Hour=EEPROM_Read(0x2000);				// ��ȡ0x2000�����ַ�����ݣ���ֵ�����ӵ�Сʱ����
	if(Clock_Hour>23)											// �����ȡ��������Сʱ��ֵ�������������¸�ֵ
	{
		Clock_Hour=12;
	}
  Clock_Minute=EEPROM_Read(0x2001);			// ��ȡ0x2001�����ַ�����ݣ���ֵ�����ӵķ��ӱ���
	if(Clock_Minute>59)										// �����ȡ�������ӷ�����ֵ�������������¸�ֵ
	{
		Clock_Minute=30;
	}
	Clock_Swt=EEPROM_Read(0x2002);				// ��ȡ0x2002�����ַ�����ݣ���ֵ�����ӵĿ��ر���
	if(Clock_Swt>1)												// �����ȡ�������ӿ�����ֵ�������������¸�ֵ
	{
		Clock_Swt=0;
	}
	
	
	while(1)
	{
		DS1302_Read_Time();				// ��ȡ��ǰʱ��оƬ��ʱ�䣬��������time_buf��
		
		ClockJudge();							// ���ӹ������ж�
		
		FlashTime();							// ˢ��ʱ����ʾ

		KeyScanf1();							// ����ɨ��(ʱ�������)
		
		KeyScanf2();							// ����ɨ��(���ӵ�����)
		
		DelayMs(100);							// ��ʱ0.1��
	}
}




