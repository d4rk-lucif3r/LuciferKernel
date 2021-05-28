/*
 *
 * FocalTech fts TouchScreen driver.
 *
 * Copyright (c) 2010-2016, Focaltech Ltd. All rights reserved.
 *
 * This software is licensed under the terms of the GNU General Public
 * License version 2, as published by the Free Software Foundation, and
 * may be copied, distributed, and modified under those terms.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 */

/*****************************************************************************
*
* File Name: focaltech_flash.c
*
* Author:    fupeipei
*
* Created:    2016-08-08
*
* Abstract:
*
* Reference:
*
*****************************************************************************/

/*****************************************************************************
* 1.Included header files
*****************************************************************************/
#include "focaltech_core.h"
#include "focaltech_flash.h"

/*****************************************************************************
* Static variables
*****************************************************************************/
struct ft_chip_t chip_types;



unsigned char CTPM_FW[] = {
#include FTS_UPGRADE_FW_APP
};

unsigned char aucFW_PRAM_BOOT[] = {
#ifdef FTS_UPGRADE_PRAMBOOT
#include FTS_UPGRADE_PRAMBOOT
#endif
};

unsigned char CTPM_LCD_CFG[] = {
#ifdef FTS_UPGRADE_LCD_CFG
#include FTS_UPGRADE_LCD_CFG
#endif
};

/*****************************************************************************
* Global variable or extern global variabls/functions
*****************************************************************************/
struct fts_upgrade_fun  fts_updatefun_curr;

struct workqueue_struct *touch_wq;
struct work_struct fw_update_work;

/*****************************************************************************
* Static function prototypes
*****************************************************************************/

/************************************************************************
* Name: fts_ctpm_upgrade_delay
* Brief: 0
* Input: 0
* Output: 0
* Return: 0
***********************************************************************/
void fts_ctpm_upgrade_delay(u32 i)
{
	do {
		i--;
	} while (i > 0);
}

/************************************************************************
* Name: fts_ctpm_i2c_hid2std
* Brief:  HID to I2C
* Input: i2c info
* Output: no
* Return: fail =0
***********************************************************************/
int fts_ctpm_i2c_hid2std(struct i2c_client *client)
{
#if (FTS_CHIP_IDC)
	return 0;
#else
	u8 buf[5] = {0};
	int bRet = 0;

	buf[0] = 0xeb;
	buf[1] = 0xaa;
	buf[2] = 0x09;
	bRet = fts_i2c_write(client, buf, 3);
	msleep(10);
	buf[0] = buf[1] = buf[2] = 0;
	fts_i2c_read(client, buf, 0, buf, 3);

	if ((0xeb == buf[0]) && (0xaa == buf[1]) && (0x08 == buf[2])) {
		FTS_DEBUG("hidi2c change to stdi2c successful!!");
		bRet = 1;
	} else {
		FTS_ERROR("hidi2c change to stdi2c error!!");
		bRet = 0;
	}

	return bRet;
#endif
}

/************************************************************************
* Name: fts_get_chip_types
* Brief: get correct chip information
* Input:
* Output:
* Return:
***********************************************************************/
void fts_get_chip_types(void)
{
	struct ft_chip_t ctype[] = FTS_CHIP_TYPE_MAPPING;
	int ic_type = 0;

	if (sizeof(ctype) != sizeof(struct ft_chip_t)) /* only one array */
		ic_type = IC_SERIALS - 1;

	chip_types = ctype[ic_type];

	FTS_INFO("CHIP TYPE ID = 0x%02x%02x", chip_types.chip_idh, chip_types.chip_idl);
}

/************************************************************************
* Name: fts_ctpm_get_upgrade_array
* Brief: decide which ic
* Input: no
* Output: get ic info in fts_updateinfo_curr
* Return: no
***********************************************************************/
void fts_ctpm_get_upgrade_array(void)
{

	FTS_FUNC_ENTER();

	fts_get_chip_types();

	fts_ctpm_i2c_hid2std(fts_i2c_client);

	/* Get functin pointer */
	memcpy(&fts_updatefun_curr, &fts_updatefun, sizeof(struct fts_upgrade_fun));

	FTS_FUNC_EXIT();
}

/************************************************************************
* Name: fts_ctpm_rom_or_pram_reset
* Brief: RST CMD(07), reset to romboot(maybe->bootloader)
* Input:
* Output:
* Return:
***********************************************************************/
void fts_ctpm_rom_or_pram_reset(struct i2c_client *client)
{
	u8 rst_cmd = FTS_REG_RESET_FW;

	FTS_INFO("[UPGRADE]******Reset to romboot/bootloader******");
	fts_i2c_write(client, &rst_cmd, 1);
	/* The delay can't be changed */
	msleep(300);
}

/************************************************************************
* Name: fts_ctpm_auto_clb_sharp
* Brief:  auto calibration
* Input: i2c info
* Output: no
* Return: 0
***********************************************************************/
int fts_ctpm_auto_clb_sharp(struct i2c_client *client)
{
#if FTS_AUTO_CLB_EN
	unsigned char uc_temp = 0x00;
	unsigned char i = 0;

	/*start auto CLB */
	msleep(200);

	fts_i2c_write_reg(client, 0, FTS_REG_WORKMODE_FACTORY_VALUE);
	/*make sure already enter factory mode */
	msleep(100);
	/*write command to start calibration */
	fts_i2c_write_reg(client, 2, 0x4);
	msleep(300);
	if ((chip_types.chip_idh == 0x11) || (chip_types.chip_idh == 0x12) || (chip_types.chip_idh == 0x13) || (chip_types.chip_idh == 0x14)) {
		for (i = 0; i < 100; i++) {
			fts_i2c_read_reg(client, 0x02, &uc_temp);
			if (0x02 == uc_temp ||
				0xFF == uc_temp) {
				break;
			}
			msleep(20);
		}
	} else {
		for (i = 0; i < 100; i++) {
			fts_i2c_read_reg(client, 0, &uc_temp);
			if (0x0 == ((uc_temp&0x70)>>4)) {
				break;
			}
			msleep(20);
		}
	}
	fts_i2c_write_reg(client, 0, 0x40);
	msleep(200);
	fts_i2c_write_reg(client, 2, 0x5);
	msleep(300);
	fts_i2c_write_reg(client, 0, FTS_REG_WORKMODE_WORK_VALUE);
	msleep(300);
#endif

	return 0;
}

/************************************************************************
* Name: fts_GetFirmwareSize
* Brief:  get file size
* Input: file name
* Output: no
* Return: file size
***********************************************************************/
int fts_GetFirmwareSize(char *firmware_name)
{
	struct file *pfile = NULL;
	struct inode *inode;
	unsigned long magic;
	off_t fsize = 0;
	char filepath[FILE_NAME_LENGTH];

	memset(filepath, 0, sizeof(filepath));
	sprintf(filepath, "%s%s", FTXXXX_INI_FILEPATH_CONFIG, firmware_name);
	if (NULL == pfile) {
		pfile = filp_open(filepath, O_RDONLY, 0);
	}
	if (IS_ERR(pfile)) {
		FTS_ERROR("error occured while opening file %s", filepath);
		return -EIO;
	}
	inode = pfile->f_path.dentry->d_inode;
	magic = inode->i_sb->s_magic;
	fsize = inode->i_size;
	filp_close(pfile, NULL);
	return fsize;
}

/************************************************************************
* Name: fts_ReadFirmware
* Brief:  read firmware buf for .bin file.
* Input: file name, data buf
* Output: data buf
* Return: 0
***********************************************************************/
int fts_ReadFirmware(char *firmware_name, unsigned char *firmware_buf)
{
	struct file *pfile = NULL;
	struct inode *inode;
	unsigned long magic;
	off_t fsize;
	char filepath[FILE_NAME_LENGTH];
	loff_t pos;
	mm_segment_t old_fs;

	memset(filepath, 0, sizeof(filepath));
	sprintf(filepath, "%s%s", FTXXXX_INI_FILEPATH_CONFIG, firmware_name);
	if (NULL == pfile) {
		pfile = filp_open(filepath, O_RDONLY, 0);
	}
	if (IS_ERR(pfile)) {
		FTS_ERROR("[UPGRADE] Error occured while opening file %s.\n", filepath);
		return -EIO;
	}
	inode = pfile->f_path.dentry->d_inode;
	magic = inode->i_sb->s_magic;
	fsize = inode->i_size;
	old_fs = get_fs();
	set_fs(KERNEL_DS);
	pos = 0;
	vfs_read(pfile, firmware_buf, fsize, &pos);
	filp_close(pfile, NULL);
	set_fs(old_fs);
	return 0;
}

/************************************************************************
* Name: fts_getsize
* Brief: 0
* Input: 0
* Output: 0
* Return: 0
***********************************************************************/
u32 fts_getsize(u8 fw_type)
{
	int fw_len = 0;

	if (fw_type == FW_SIZE)
		fw_len = sizeof(CTPM_FW);
#if FTS_CHIP_IDC
	else if (fw_type == PRAMBOOT_SIZE)
		fw_len = sizeof(aucFW_PRAM_BOOT);
#endif
#if (FTS_CHIP_TYPE == _FT8006)
	else if (fw_type == LCD_CFG_SIZE)
		fw_len = sizeof(CTPM_LCD_CFG);
#endif

	return fw_len;
}

/************************************************************************
* Name: fts_ctpm_get_pram_or_rom_id
* Brief: 0
* Input: 0
* Output: 0
* Return: 0
***********************************************************************/
enum FW_STATUS fts_ctpm_get_pram_or_rom_id(struct i2c_client *client)
{
	u8 buf[4];
	u8 reg_val[2] = {0};
	enum FW_STATUS inRomBoot = FTS_RUN_IN_ERROR;

	fts_ctpm_i2c_hid2std(client);

	/*Enter upgrade mode*/
	/*send 0x55 in time windows*/
	buf[0] = FTS_UPGRADE_55;
	buf[1] = FTS_UPGRADE_AA;
	fts_i2c_write(client, buf, 2);

	msleep(20);

	buf[0] = 0x90;
	buf[1] = buf[2] = buf[3] = 0x00;
	fts_i2c_read(client, buf, 4, reg_val, 2);

	FTS_DEBUG("[UPGRADE] ROM/PRAM/Bootloader id:0x%02x%02x", reg_val[0], reg_val[1]);
	if ((reg_val[0] == 0x00) || (reg_val[0] == 0xFF)) {
		inRomBoot = FTS_RUN_IN_ERROR;
	} else if (reg_val[0] == chip_types.pramboot_idh && reg_val[1] == chip_types.pramboot_idl) {
		inRomBoot = FTS_RUN_IN_PRAM;
	} else if (reg_val[0] == chip_types.rom_idh && reg_val[1] == chip_types.rom_idl) {
		inRomBoot = FTS_RUN_IN_ROM;
	} else if (reg_val[0] == chip_types.bootloader_idh && reg_val[1] == chip_types.bootloader_idl) {
		inRomBoot = FTS_RUN_IN_BOOTLOADER;
	}

	return inRomBoot;
}

/************************************************************************
* Name: fts_ctpm_get_app_ver
* Brief:  get app file version
* Input:
* Output:
* Return: fw version
***********************************************************************/
int fts_ctpm_get_app_ver(void)
{
	int i_ret = 0;

	if (fts_updatefun_curr.get_app_i_file_ver)
		i_ret = fts_updatefun_curr.get_app_i_file_ver();

	if (i_ret < 0)
		i_ret = 0;

	return i_ret;
}

/************************************************************************
* Name: fts_ctpm_fw_upgrade
* Brief:  fw upgrade entry funciotn
* Input:
* Output:
* Return: 0  - upgrade successfully
*         <0 - upgrade failed
***********************************************************************/
int fts_ctpm_fw_upgrade(struct i2c_client *client)
{
	int i_ret = 0;

	if (fts_updatefun_curr.upgrade_with_app_i_file)
		i_ret = fts_updatefun_curr.upgrade_with_app_i_file(client);

	return i_ret;
}

/************************************************************************
* Name: fts_ctpm_fw_upgrade
* Brief:  fw upgrade entry funciotn
* Input:
* Output:
* Return: 0  - upgrade successfully
*         <0 - upgrade failed
***********************************************************************/
int fts_ctpm_lcd_cfg_upgrade(struct i2c_client *client)
{
	int i_ret = 0;

	if (fts_updatefun_curr.upgrade_with_lcd_cfg_i_file)
		i_ret = fts_updatefun_curr.upgrade_with_lcd_cfg_i_file(client);

	return i_ret;
}

#if (!(FTS_UPGRADE_STRESS_TEST))
/************************************************************************
* Name: fts_ctpm_check_fw_status
* Brief: Check App is valid or not
* Input:
* Output:
* Return: -EIO - I2C communication error
*         FTS_RUN_IN_APP - APP valid
*         0 - APP invalid
***********************************************************************/
static int fts_ctpm_check_fw_status(struct i2c_client *client)
{
	u8 chip_id1 = 0;
	u8 chip_id2 = 0;
	int fw_status = FTS_RUN_IN_ERROR;
	int i = 0;
	int ret = 0;
	int i2c_noack_retry = 0;

	for (i = 0; i < 5; i++) {
		ret = fts_i2c_read_reg(client, FTS_REG_CHIP_ID, &chip_id1);
		if (ret < 0) {
			i2c_noack_retry++;
			continue;
		}
		ret = fts_i2c_read_reg(client, FTS_REG_CHIP_ID2, &chip_id2);
		if (ret < 0) {
			i2c_noack_retry++;
			continue;
		}

		if ((chip_id1 == chip_types.chip_idh)
#if FTS_CHIP_IDC
			&& (chip_id2 == chip_types.chip_idl)
#endif
		   ) {
			fw_status = FTS_RUN_IN_APP;
			break;
		}
	}

	FTS_DEBUG("[UPGRADE]: chip_id = %02x%02x, chip_types.chip_idh = %02x%02x",
			 chip_id1, chip_id2, chip_types.chip_idh, chip_types.chip_idl);

	/* I2C No ACK 5 times, then return -EIO */
	if (i2c_noack_retry >= 5)
		return -EIO;

	/* I2C communication ok, but not get correct ID, need check pram/rom/bootloader */
	if (i >= 5)
		fw_status = fts_ctpm_get_pram_or_rom_id(client);

	return fw_status;
}

/************************************************************************
* Name: fts_ctpm_check_vendorid_fw
* Brief: Check vendor id is valid or not
* Input:
* Output:
* Return: 1 - vendor id valid
*         0 - vendor id invalid
***********************************************************************/
static int fts_ctpm_check_vendorid_fw(struct i2c_client *client)
{
#if FTS_GET_VENDOR_ID
	u8 vendor_id;
	fts_i2c_read_reg(client, FTS_REG_VENDOR_ID, &vendor_id);

	FTS_DEBUG("[UPGRADE] tp_vendor_id=%x, FTS_VENDOR_1_ID=%x, FTS_VENDOR_2_ID=%x", vendor_id, FTS_VENDOR_1_ID, FTS_VENDOR_2_ID);
	if ((vendor_id == FTS_VENDOR_1_ID) || (vendor_id == FTS_VENDOR_2_ID))
		return 1;
	else
		return 0;
#else
	return 1;
#endif
}

/************************************************************************
* Name: fts_ctpm_check_fw_ver
* Brief: Check vendor id is valid or not
* Input:
* Output:
* Return: 1 - vendor id valid
*         0 - vendor id invalid
***********************************************************************/
	extern u8 fw_ver;

#if FTS_AUTO_UPGRADE_EN

extern char TP_vendor;
static char tp_info_summary[80] = "";
#endif
 static int fts_ctpm_check_fw_ver(struct i2c_client *client)
{

	u8 uc_tp_fm_ver;
	u8 uc_host_fm_ver = 0;


	fts_i2c_read_reg(client, FTS_REG_FW_VER, &uc_tp_fm_ver);
	uc_host_fm_ver = fts_ctpm_get_app_ver();

	FTS_DEBUG("[UPGRADE]: uc_tp_fm_ver = 0x%x, uc_host_fm_ver = 0x%x!!", uc_tp_fm_ver, uc_host_fm_ver);

	printk("fw_ver= %d\n", uc_tp_fm_ver);


	if (uc_tp_fm_ver < uc_host_fm_ver)
		return 1;
	else
		return 0;
}

/************************************************************************
* Name: fts_ctpm_check_need_upgrade
* Brief:
* Input:
* Output:
* Return: 1 - Need upgrade
*         0 - No upgrade
***********************************************************************/
static int fts_ctpm_check_need_upgrade(struct i2c_client *client)
{
	int fw_status = 0;
	int bUpgradeFlag = false;

	FTS_FUNC_ENTER();

	/* 1. veriry FW APP is valid or not */
	fw_status = fts_ctpm_check_fw_status(client);
	FTS_DEBUG("[UPGRADE]: fw_status = %d!!", fw_status);
	if (fw_status < 0) {
		/* I2C no ACK, return immediately */
		FTS_ERROR("[UPGRADE]******I2C NO ACK,exit upgrade******");
		return -EIO;
	} else if (fw_status == FTS_RUN_IN_ERROR) {
		FTS_ERROR("[UPGRADE]******IC Type Fail******");
	} else if (fw_status == FTS_RUN_IN_APP) {
		FTS_INFO("[UPGRADE]**********FW APP valid**********");

		/* 2. check vendor id is valid or not */
		if (fts_ctpm_check_vendorid_fw(client) == 0) {
			FTS_DEBUG("[UPGRADE]******Vendor ID in FW is invalid******");
			return false;
		}

		if (fts_ctpm_check_fw_ver(client) == 1) {
			FTS_DEBUG("[UPGRADE]**********need upgrade fw**********");
			bUpgradeFlag = true;
		} else {
			FTS_DEBUG("[UPGRADE]**********Don't need upgrade fw**********");
			bUpgradeFlag = false;
		}
	} else {
		/* if app is invalid, reset to run ROM */
		FTS_INFO("[UPGRADE]**********FW APP invalid**********");
		fts_ctpm_rom_or_pram_reset(client);

		bUpgradeFlag = true;
	}

	fts_ctpm_check_fw_ver(client);

	FTS_FUNC_EXIT();

	return bUpgradeFlag;
}

/************************************************************************
* Name: fts_ctpm_auto_upgrade
* Brief:  auto upgrade
* Input:
* Output:
* Return: 0 - no upgrade
***********************************************************************/
int fts_ctpm_auto_upgrade(struct i2c_client *client)
{
	u8 uc_tp_fm_ver;
	int i_ret = 0;
	int bUpgradeFlag = false;
	u8 uc_upgrade_times = 0;

	FTS_DEBUG("[UPGRADE]********************check upgrade need or not********************");
	bUpgradeFlag = fts_ctpm_check_need_upgrade(client);
	FTS_DEBUG("[UPGRADE]**********bUpgradeFlag = 0x%x**********", bUpgradeFlag);

	if (bUpgradeFlag <= 0) {
		FTS_DEBUG("[UPGRADE]**********No Upgrade, exit**********");
		return 0;
	} else {
		/* FW Upgrade */
		do {
			uc_upgrade_times++;
			FTS_DEBUG("[UPGRADE]********************star upgrade(%d)********************", uc_upgrade_times);

			i_ret = fts_ctpm_fw_upgrade(client);
			if (i_ret == 0) {
				/* upgrade success */
				fts_i2c_read_reg(client, FTS_REG_FW_VER, &uc_tp_fm_ver);
				FTS_DEBUG("[UPGRADE]********************Success upgrade to new fw version 0x%x********************", uc_tp_fm_ver);

				fts_ctpm_auto_clb_sharp(client);
				break;
			} else {
				/* upgrade fail, reset to run ROM BOOT..
				* if app in flash is ok, TP will work success
				*/
				FTS_ERROR("[UPGRADE]********************upgrade fail, reset now********************");
				fts_ctpm_rom_or_pram_reset(client);
			}
		} while (uc_upgrade_times < 2);  /* if upgrade fail, upgrade again. then return */
	}

	return i_ret;
}
#endif

#if FTS_AUTO_UPGRADE_EN

#if FTS_LOCK_DOWN_INFO
extern char ftp_lockdown_info[128];
#endif
static void fts_ctpm_update_work_func(struct work_struct *work)
{
	int i_ret = 0;
	char tp_temp_info[80];

#if FTS_LOCK_DOWN_INFO
	unsigned char auc_i2c_write_buf[10];
	u8  r_buf[10] = {0};
	char err = -1;
#endif

	FTS_DEBUG("[UPGRADE]******************************FTS enter upgrade******************************");
	fts_irq_disable();

	/* esd check */
#if FTS_ESDCHECK_EN
	fts_esdcheck_switch(DISABLE);
#endif

	i_ret = fts_ctpm_auto_upgrade(fts_i2c_client);
	if (i_ret < 0)
		FTS_ERROR("[UPGRADE]**********TP FW upgrade failed**********");

#if FTS_AUTO_UPGRADE_FOR_LCD_CFG_EN
	msleep(2000);

	/* lcd_cfg upgrade */
	i_ret = fts_ctpm_lcd_cfg_upgrade(fts_i2c_client);
	if (i_ret < 0)
		FTS_ERROR("[UPGRADE]**********LCD cfg upgrade failed*********");
#endif
	fts_i2c_read_reg(fts_i2c_client, FTS_REG_FW_VER, &fw_ver);

	printk("fw_ver: %d",  fw_ver);

	if (TP_vendor == 1) {
		strcpy(tp_info_summary, "[Vendor]Sharp, [IC]FT8716, [FW]Ver");
	} else if (TP_vendor == 2) {
		 strcpy(tp_info_summary, "[Vendor]Eggb, [IC]FT8716, [FW]Ver");
	} else{
		strcpy(tp_info_summary, "[Vendor]Unknown, [IC]FT8716, [FW]Ver");
	}
	sprintf(tp_temp_info, "%d", fw_ver);
		strcat(tp_info_summary, tp_temp_info);
	strcat(tp_info_summary, "\0");

#ifdef FTS_LOCK_DOWN_INFO

	if (strncmp("3833", ftp_lockdown_info, 4)) {
		err = fts_i2c_write_reg(fts_i2c_client, 0x90, 0x20);
		if (err < 0)
			printk("[FTS] i2c write 0x90 err\n");

		msleep(5);
		auc_i2c_write_buf[0] = 0x99;
		err = fts_i2c_read(fts_i2c_client, auc_i2c_write_buf, 1, r_buf, 8);
		if (err < 0)
			printk("[FTS] i2c read 0x99 err\n");

		sprintf(ftp_lockdown_info, "%02x%02x%02x%02x%02x%02x%02x%02x", \
				r_buf[0], r_buf[1], r_buf[2], r_buf[3], r_buf[4], r_buf[5], r_buf[6], r_buf[7]);

		printk(" ft8716 get lockdown info after upgrade, tp_lockdown_info=%s\n", ftp_lockdown_info);
	} else{
		printk("FT8716 lockdown info is OK\n");
	}
#endif

#if FTS_ESDCHECK_EN
	fts_esdcheck_switch(ENABLE);
#endif
	fts_irq_enable();

	FTS_DEBUG("[UPGRADE]******************************FTS exit upgrade******************************");
}

/*****************************************************************************
*  Name: fts_ctpm_upgrade_init
*  Brief:
*  Input:
*  Output:
*  Return:
*****************************************************************************/
void fts_ctpm_upgrade_init(void)
{
	FTS_FUNC_ENTER();

	touch_wq = create_singlethread_workqueue("touch_wq");
	if (touch_wq) {
		INIT_WORK(&fw_update_work, fts_ctpm_update_work_func);
		queue_work(touch_wq, &fw_update_work);
	} else {
		FTS_ERROR("[UPGRADE]create_singlethread_workqueue failed\n");
	}

	FTS_FUNC_EXIT();
}

/*****************************************************************************
*  Name: fts_ctpm_upgrade_exit
*  Brief:
*  Input:
*  Output:
*  Return:
*****************************************************************************/
void fts_ctpm_upgrade_exit(void)
{
	FTS_FUNC_ENTER();
	destroy_workqueue(touch_wq);
	FTS_FUNC_EXIT();
}

#endif  /* #if FTS_AUTO_UPGRADE_EN */
