// Choose coil number and send current command
// Command DAQ
// #include <stdio.h>
// #include <math.h>
// #include <stdlib.h>

// extern "C" {
// #include "pmd.h"
// #include "usb-3100.h"
// #include "unistd.h"
// }

#include <stdlib.h>
#include <stdio.h>
#include <iostream>
#include <vector>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <ctype.h>
#include <stdint.h>
#include <math.h>
#include "pmd.h"
#include "usb-3100.h"

#define MAX_STR 255


#define PI 3.14159265


int main(int argc, char** argv) 
{
  
  hid_device *hid = 0x0;
  float volts, voltsoff;
  int flag;
  uint8_t channel, fwd_byte, rev_byte, update; //range
  int8_t range{1};
  int temp, i;
  int ch, stop_ch;
  bool loop = false;
  uint16_t value, valueoff;
  wchar_t serial[64];
  wchar_t wstr[MAX_STR];
  double amplitude, wave_freq, update_rate, dt, cycle_length, total_time;
  int ret;
  uint8_t memory[62];
  std::vector<float> buffer;
  std::vector<float> buffer2;
  std::vector<int>::iterator It; // declare a general iterator

  ret = hid_init();

  if (ret < 0) {
    fprintf(stderr, "hid_init failed with return code %d\n", ret);
    return -1;
  }


  if ((hid = hid_open(MCC_VID, USB3103_PID, NULL)) > 0) {
    printf("USB 3103 Device is found!\n");
  } 
  else {
    fprintf(stderr, "USB 31XX  not found.\n");
    return 0;    
  }

 /* config mask 0x01 means all inputs */
  usbDConfigPort_USB31XX(hid, DIO_DIR_OUT);
  usbDOut_USB31XX(hid, 0);

  // Configure all analog channels for 0-10V output
  for (i = 0; i < 8; i++) {
    usbAOutConfig_USB31XX(hid, i, UP_10_00V); // BP_10_00V for +/- 10 V
  }

  update_rate = 50; // update current through coils at 50 Hz (50 times per second)

  while(1) {
  printf("\nDAQ Update for Helical Swimmer OL Control\n");
  printf("----------------\n");
  printf("Hit 'i' to initialize analog voltage output.\n");
  printf("Hit 'o' for forward (North) swimming.\n");
  printf("Hit 'd' to test digital output\n");
  printf("Hit 'a' to test analog output\n");
  printf("Hit 'e' to exit\n");

  while((ch = getchar()) == '\0' ||
    ch == '\n');

  switch(ch) {
    case 'i':
    printf("Enter frequency [0-30Hz]: \n");
    scanf("%d", &temp);
    wave_freq = (uint8_t) temp; //user-defined frequency of sine wave xx Hz = xx cycle / sec
    amplitude = 1.0;
    // float buffer[50]; // buffer size should be the same as the update rate
    // float buffer2[50]; // buffer size should be the same as the update rate


    dt = 1/update_rate; // time between samples
    cycle_length = 2*PI; // sine wave has a cycle length of 2pi
    total_time = 1; // 1 second; final time for 1 cycle/ 1 waveform.

    for (int i = 0; i<=update_rate; i++){
        std::cout << i << ".\n";
        // buffer[i] = amplitude * sin(wave_freq*(2 * PI) * (i / update_rate));    
        // buffer2[i] = amplitude * sin(wave_freq * (2 * PI) *(i / update_rate) - PI/2);
        buffer.push_back (amplitude * sin(wave_freq*(2 * PI) * (i / update_rate)));
        buffer2.push_back (amplitude * sin(wave_freq * (2 * PI) *(i / update_rate) - PI/2));
        std::cout << buffer[i] << ".\n";
        std::cout << buffer2[i] << ".\n";
    }

    std::cout << "size of buffer: " << buffer.size() << std::endl;
    std::cout << "size of buffer2: " << buffer2.size() << std::endl;

    break;
    case 'o':
      printf("Testing forward swimming.\n");
      // Initialize Digital Output Pin for Forward Current Direction
      fwd_byte = 0;
      rev_byte = 0xff;
      usbDConfigPort_USB31XX(hid, DIO_DIR_OUT);

      range = (uint8_t) 0; // 0 = 0-10V, 1 = +/- 10V  2 = 0-20 mA
      for (int i = 0; i<=update_rate; i++){
        std::cout << buffer[i] << ".\n";
        if (buffer[i] < 0) {
          // flip DIO pin to reverse current 
          usbDOut_USB31XX(hid, rev_byte);
          volts = buffer[i] * -1;
        }
        else {
          usbDOut_USB31XX(hid, fwd_byte);
          volts = buffer[i];
        }
          channel = (uint8_t) 0; // channel on DAQ for analog voltage output 0 - 15

          value = volts_USB31XX(range, volts);
          usbAOutConfig_USB31XX(hid, channel, range);
          usbAOut_USB31XX(hid, channel, value, 0);
          // std::cout << buffer2[i] << ".\n";
          usleep(1000000);
        }

      volts = 0;
      value = volts_USB31XX(range, volts);
      usbAOutConfig_USB31XX(hid, channel, range);
      usbAOut_USB31XX(hid, channel, value, 0);
      break;
    case 'a':
      printf("Testing the analog output for a single channel.\n");
      printf("Enter channel [0-15]: ");
      scanf("%d", &temp);
      channel = (uint8_t) temp;
      printf("Enter a range: 0 = 0-10V, 1 = +/- 10V, 2 = 0-20mA ");
      scanf("%d", &temp);
      range = (uint8_t) temp;
      printf("Enter a voltage: ");
      scanf("%f", &volts);
      value = volts_USB31XX(range, volts);
      usbAOutConfig_USB31XX(hid, channel, range);
      usbAOut_USB31XX(hid, channel, value, 0);
      break;
    case 'd':
      printf("\nTesting Digital I/O....\n");
      printf("Enter a byte number [0-0xff]: " );
      scanf("%x", &temp);
      usbDConfigPort_USB31XX(hid, DIO_DIR_OUT);
      usbDOut_USB31XX(hid, (uint8_t)temp);
      break;
    case 'e':
      hid_close(hid);
      hid_exit();
      return 0;
      break;
    }
  }

  // unsigned int usecs;
  // usecs = 2000;
  // sleep(usecs);
  
  return 0;
}
