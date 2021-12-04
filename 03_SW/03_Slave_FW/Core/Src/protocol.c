/*
 * protocol.c
 *
 *  Created on: Nov 26, 2021
 *      Author: hoadv
 */

#include "protocol.h"

uint8_t encode_msg(driver_t *driver, uint8_t dev_id, uint8_t *msg)
{
	msg[0] = dev_id;
	msg[1] = 0x05;
	msg[2] = driver->btn;
	return 1;
}

/*
 *		msg: | ADDR | Data[] |
 */
uint8_t decode_msg(driver_t *driver, uint8_t *msg, uint8_t len)
{
	if (len < sizeof(driver_t) && len > 0)
	{
		memcpy(&((uint8_t *)driver)[msg[0]], &msg[1], len - 1);
		return 1;
	}
	return 0;
}
