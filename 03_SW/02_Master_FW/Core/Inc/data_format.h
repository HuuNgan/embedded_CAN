#ifndef __DATA_FORMAT
#define __DATA_FORMAT

#include <stdint.h>

#define STX     (0x02)
#define ETX     (0x0A)

#define LED_MODE_RAINBOW    (0)
#define LED_MODE_RANDOM     (1)
#define LED_MODE_SINGLE     (2)
#define LED_MODE_STOP       (3)

#define PERIPH_TYPE_NEO     (0)
#define PERIPH_TYPE_LED     (1)
#define PERIPH_TYPE_BTN     (2)

#define DATA_LENGTH_OFFSET  (1)
#define CAN_ID_OFFSET       (2)
#define PERIPH_TYPE_OFFSET  (3)
#define MODE_OFFSET         (4)
#define COLOR_OFFSET        (5)

#define NEO_MODE_REG_ADDR   (0x00)
#define LED_REG_ADDR        (0x04)
#define BTN_REG_ADDR        (0x05)

typedef struct
{
  uint8_t RegAddr;
  uint8_t ButtonState;
} CAN_RxFrame_t;

typedef struct
{
  uint8_t StartOfFrame;
  uint8_t DataLength;
  uint8_t CAN_ID;
  uint8_t PeriphType;
  uint8_t Mode;
  uint8_t ColorRed;
  uint8_t ColorGreen;
  uint8_t ColorBlue;
  uint8_t EndOfFrame;
} UART_FRAME_t;

typedef union
{
  uint8_t array[9];
  UART_FRAME_t Frame;
} UartRxFrame_t;


#endif
