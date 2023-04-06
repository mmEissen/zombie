/**************************************************************************/
/*!
    @file     iso14443a_uid.pde
    @author   Adafruit Industries
	@license  BSD (see license.txt)

    This example will attempt to connect to an ISO14443A
    card or tag and retrieve some basic information about it
    that can be used to determine what type of card it is.

    Note that you need the baud rate to be 115200 because we need to print
	out the data and read from the card at the same time!

This is an example sketch for the Adafruit PN532 NFC/RFID breakout boards
This library works with the Adafruit NFC breakout
  ----> https://www.adafruit.com/products/364

Check out the links above for our tutorials and wiring diagrams
These chips use SPI or I2C to communicate.

Adafruit invests time and resources providing this open source code,
please support Adafruit and open-source hardware by purchasing
products from Adafruit!

*/
/**************************************************************************/
#include <Wire.h>
#include <SPI.h>
#include <Adafruit_PN532.h>

#define PN532_SCK_1  (2)
#define PN532_MISO_1 (3)
#define PN532_MOSI_1 (4)
#define PN532_SS_1   (5)

#define PN532_SCK_2  (6)
#define PN532_MISO_2 (7)
#define PN532_MOSI_2 (8)
#define PN532_SS_2   (9)

Adafruit_PN532 nfc_1(PN532_SCK_1, PN532_MISO_1, PN532_MOSI_1, PN532_SS_1);
Adafruit_PN532 nfc_2(PN532_SCK_2, PN532_MISO_2, PN532_MOSI_2, PN532_SS_2);

#define MAX_UID_LENGTH (7)

uint8_t no_uid[MAX_UID_LENGTH] = { 0 };

uint8_t uid_1[MAX_UID_LENGTH] = { 0 };
uint8_t length_1 = 7;
uint8_t uid_2[MAX_UID_LENGTH] = { 0 };
uint8_t length_2 = 7;

void setup(void) {
  Serial.begin(19200);
  while (!Serial) delay(10); // for Leonardo/Micro/Zero

  nfc_1.begin();
  nfc_2.begin();

  uint32_t versiondata_1 = nfc_1.getFirmwareVersion();
  if (! versiondata_1) {
    Serial.println("ERROR 1");
    while (1); // halt
  }

  uint32_t versiondata_2 = nfc_2.getFirmwareVersion();
  if (! versiondata_2) {
    Serial.println("ERROR 2");
    while (1); // halt
  }


  // Set the max number of retry attempts to read from a card
  // This prevents us from waiting forever for a card, which is
  // the default behaviour of the PN532.
  nfc_1.setPassiveActivationRetries(0xFF);
  nfc_2.setPassiveActivationRetries(0xFF);

  Serial.println("START");
}


void print_uid(uint8_t* uid, uint8_t uid_length) {
  for (uint8_t i=0; i < uid_length; i++)
  {
    if (i != 0) {
      Serial.print(":");
    }
    Serial.print(uid[i], HEX);
  }
}


bool is_same_uid(uint8_t* left, uint8_t* right) {
  return (memcmp(left, right, MAX_UID_LENGTH) == 0);
}


void check_reader(Adafruit_PN532 &nfc, uint8_t* current_uid, uint8_t &current_length, uint8_t reader_id) {
  boolean success;
  uint8_t new_uid[MAX_UID_LENGTH] = { 0 };
  uint8_t new_length;

  success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, &new_uid[0], &new_length, 100);

  if (success) {
    if (!is_same_uid(new_uid, current_uid)) {
      if( !is_same_uid(no_uid, current_uid) ) {
        Serial.print("-");
        Serial.print(reader_id, HEX);
        Serial.print(" ");
        print_uid(current_uid, current_length);
        Serial.println("");
      }

      memcpy(current_uid, new_uid, MAX_UID_LENGTH);
      current_length = new_length;

      Serial.print("+");
      Serial.print(reader_id, HEX);
      Serial.print(" ");
      print_uid(current_uid, current_length);
      Serial.println("");
    }
  }
  else
  {
    if( !is_same_uid(no_uid, current_uid) ) {
      Serial.print("-");
      Serial.print(reader_id, HEX);
      Serial.print(" ");
      print_uid(current_uid, current_length);
      Serial.println("");

      memcpy(current_uid, no_uid, MAX_UID_LENGTH);
    }
  }
}


void loop(void) {
  check_reader(nfc_1, uid_1, length_1, 1);
  check_reader(nfc_2, uid_2, length_2, 2);
}
