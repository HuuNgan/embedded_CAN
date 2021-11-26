#ifndef __DATA_FORMAT
#define __DATA_FORMAT

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

#endif
