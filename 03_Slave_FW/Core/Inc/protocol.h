/*
 * protocol.h
 *
 *  Created on: Nov 26, 2021
 *      Author: hoadv
 */

#ifndef INC_PROTOCOL_H_
#define INC_PROTOCOL_H_

#include <stdint.h>

typedef struct {
	uint8_t MODE; 	// 0x00
	uint8_t R;		// 0x01
	uint8_t G;		// 0x02
	uint8_t B;
	uint8_t led;	// 0x04
	uint8_t btn;	// 0x05
} driver_t;

uint8_t encode_msg(driver_t *driver, uint8_t *msg);
uint8_t decode_msg(driver_t *driver, uint8_t *msg, uint8_t len);

#endif /* INC_PROTOCOL_H_ */
