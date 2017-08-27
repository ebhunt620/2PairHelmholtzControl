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
#include <time.h>
#include <chrono>
#include "pmd.h"
#include "usb-3100.h"

#define MAX_STR 255


#define PI 3.14159265


int main(int argc, char** argv) 
{
  
  hid_device *hid = 0x0;
  float volts, voltsoff, volts2, temp_volts;
  int flag;
  uint8_t channel, fwd_byte, rev_byte, update, dpinz, dpinx, direction; //range
  int8_t range{1};
  int temp_swim_direction, temp_range, temp, temp_channel, i, temp_num_sec;
  int ch, stop_ch, num_sec;
  bool loop = false;
  uint16_t value, valueoff;
  wchar_t serial[64];
  wchar_t wstr[MAX_STR];
  double amplitude, update_rate, cycle_length, total_time; //wave_freq
  unsigned int dt;
  float wave_freq, temp_freq;
  int ret, swim_direction;
  uint8_t memory[62];
  struct timeval start, end, start1, end1;
  long seconds, useconds;
  double mtime;    
  std::vector<float> buffer;
  std::vector<float> buffer2;
  // std::vector<uint16_t> valueZ;
  // std::vector<uint16_t> valueX;
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

  // SINE WAVE DEFINITIONS
  update_rate = 100; // update current through coils at 50 Hz (50 times per second)
  amplitude = 1.0;
  cycle_length = 2*PI; // sine wave has a cycle length of 2pi

  // DIGITAL PIN DEFINITIONS
  dpinz = 4;
  dpinx = 2;
  direction = 0;

  while(1) {
  printf("\nDAQ Update for Helical Swimmer OL Control\n");
  printf("----------------\n");
  printf("Hit 'i' to initialize analog voltage output and to choose swimming direction.\n");
  printf("Hit 'o' to start swimming.\n");
  printf("Hit 't' to test analog output of sine wave in current buffer.\n");
  printf("Hit 'd' to test digital output.\n");
  printf("Hit 'a' to test analog output.\n");
  printf("Hit 'r' to reset DAQ channels to 0 volts.\n");
  printf("Hit 'e' to exit\n");

  while((ch = getchar()) == '\0' ||
    ch == '\n');

  switch(ch) {
    case 'i':
    printf("Enter frequency [0-30Hz]: \n");
    scanf("%f", &temp_freq);
    wave_freq = (float) temp_freq; //user-defined frequency of sine wave xx Hz = xx cycle / sec
    std::cout << wave_freq << std::endl;
    printf("Enter 1 or 2 for direction [1: North, 2:South]: \n");
    scanf("%i", &temp_swim_direction);
    swim_direction = (int) temp_swim_direction;
    std::cout<< swim_direction << std::endl;
    printf("Enter number of seconds to run the swimmer [1-60]: \n");
    scanf("%i",&temp_num_sec);
    num_sec = (int) temp_num_sec;
    
    // 1 cycle = 1 waveform
    // flush buffer
    buffer.clear();
    buffer2.clear();
    std::cout << "buffer:" << "buffer2:"  << ".\n";
    if (swim_direction == 1){
	    for (int i = 0; i<=(update_rate*num_sec); i++){
	        //std::cout << i << ".\n";
	        // buffer[i] = amplitude * sin(wave_freq*(2 * PI) * (i / update_rate));    
	        // buffer2[i] = amplitude * sin(wave_freq * (2 * PI) *(i / update_rate) - PI/2);
	        buffer.push_back (amplitude * sin(wave_freq*(2 * PI) * (i / update_rate)));
	        buffer2.push_back (amplitude * sin(wave_freq * (2 * PI) *(i / update_rate) - 3*PI/2));
	        std::cout << buffer[i]<< "  " << buffer2[i] << "\n";
	    }
	}else {
		for (int i = 0; i<=(update_rate*num_sec); i++){
	        //std::cout << i << ".\n";
	        // buffer[i] = amplitude * sin(wave_freq*(2 * PI) * (i / update_rate));    
	        // buffer2[i] = amplitude * sin(wave_freq * (2 * PI) *(i / update_rate) - PI/2);
	        buffer.push_back (amplitude * sin(wave_freq*(2 * PI) * (i / update_rate)));
	        buffer2.push_back (amplitude * sin(wave_freq * (2 * PI) *(i / update_rate) - PI/2));
	        std::cout << buffer[i] << "  " << buffer2[i] << "\n";
	    }
	}
    std::cout << "size of buffer: " << buffer.size() << std::endl;
    std::cout << "size of buffer2: " << buffer2.size() << std::endl;

    // Pre-compute voltage conversion for analog output
    // for (int i = 0; i<=(update_rate*num_sec);i++){
    // 	if (buffer[i] < 0){
    // 		volts = buffer[i] * -1;
    // 	}else{
    // 		volts = buffer[i];
    // 	}
    // 	if (buffer2[i] < 0){
    // 		volts2 = buffer2[i] * -1;
    // 	}else{
    // 		volts2 = buffer2[i];
    // 	}
    // 	valueZ.push_back (volts_USB31XX(range, volts));
    // 	valueX.push_back (volts_USB31XX(range, volts2));
    // 	std::cout << valueZ[i] << "  " << valueX[i] << "\n";
    // }
    // std::cout << "size of valueZ: " << valueZ.size() << std::endl;
    // std::cout << "size of valueX: " << valueX.size() << std::endl;

    break;
    case 'o':
      printf("Run through buffer. GO Swim.\n");
      // Initialize Digital Output Pin for Forward Current Direction
      fwd_byte = 0;
      rev_byte = 0xff;
      usbDConfigPort_USB31XX(hid, DIO_DIR_OUT);
      // usbDConfigBit_USB31XX(hid, dpinz, direction);
      // usbDConfigBit_USB31XX(hid, dpinx, direction);
      range = (uint8_t) 0; // 0 = 0-10V, 1 = +/- 10V  2 = 0-20 mA
      dt = 1/update_rate*1000000;
      gettimeofday(&start, NULL);
	
	  for (int i = 0; i<=(update_rate*num_sec); i++){
	    //std::cout << buffer[i] << " " << buffer2[i] << ".\n";
	    auto start_time = std::chrono::high_resolution_clock::now();
	    if (buffer[i] < 0) {
	      // flip DIO pin to reverse current 
	      usbDBitOut_USB31XX(hid, dpinz, rev_byte);
	      //usbDOut_USB31XX(hid, rev_byte);
	      volts = buffer[i] * -1;
	    }else {
	      usbDBitOut_USB31XX(hid, dpinz, fwd_byte);
	      //usbDOut_USB31XX(hid, fwd_byte);
	      volts = buffer[i];
	    }
	    if (buffer2[i] < 0) {
	    	// flip DIO pin to reverse current 
	    	usbDBitOut_USB31XX(hid, dpinx, rev_byte);
	    	volts2 = buffer2[i] * -1;
	    }
	    else {
	      usbDBitOut_USB31XX(hid, dpinx, fwd_byte);
	      //usbDOut_USB31XX(hid, fwd_byte);
	      volts2 = buffer2[i];
	    }
	      channel = (uint8_t) 0; // channel on DAQ for analog voltage output 0 - 15

	      value = volts_USB31XX(range, volts);
	      //usbAOutConfig_USB31XX(hid, channel, range); Doing this each time adds an extra 5ms to the loop
	      usbAOut_USB31XX(hid, channel, value, 0);

	      channel = (uint8_t) 2; // channel on DAQ for analog voltage output 0 - 15

	      value = volts_USB31XX(range, volts2);
	      //usbAOutConfig_USB31XX(hid, channel, range); Doing this each time adds an extra 5ms to the loop
	      usbAOut_USB31XX(hid, channel, value, 0);

	      // std::cout << buffer2[i] << ".\n";
	      auto current_time = std::chrono::high_resolution_clock::now();
          auto diff = std::chrono::duration_cast<std::chrono::microseconds>(current_time - start_time).count();
          if ((dt-diff)>0){

          usleep(dt-diff);
          }else{
          	usleep(dt);
          }
	    }
    	gettimeofday(&end, NULL);
    	seconds  = end.tv_sec  - start.tv_sec;
    	useconds = end.tv_usec - start.tv_usec;

    	mtime = seconds + useconds/1000000.0;

    	printf("Elapsed time: %5.6f seconds\n", mtime);
    break;
      case 't':
      printf("Testing analog output sine wave.\n");
      range = (uint8_t) 0; // 0 = 0-10V, 1 = +/- 10V  2 = 0-20 mA
      dt = 1/update_rate*1000000;
      gettimeofday(&start1, NULL);
	  for (int i = 0; i<=(update_rate*num_sec); i++){
	  	  auto start_time = std::chrono::high_resolution_clock::now();
	    if (buffer[i] < 0) {
	      volts = buffer[i] * -1;
	    }else {
	      volts = buffer[i];
	    }
	    if (buffer2[i] < 0) {
	    	volts2 = buffer2[i] * -1;
	    }
	    else {
	      volts2 = buffer2[i];
	    }
	      channel = (uint8_t) 7; // channel on DAQ for analog voltage output 0 - 15

	      value = volts_USB31XX(range, volts);
	      //usbAOutConfig_USB31XX(hid, channel, range); do this each time adds an extra 5ms
	      usbAOut_USB31XX(hid, channel, volts, 0);

	      channel = (uint8_t) 5; // channel on DAQ for analog voltage output 0 - 15

	      value = volts_USB31XX(range, volts2);
	      //usbAOutConfig_USB31XX(hid, channel, range); Doing this each time adds an extra 5ms to the loop
	      usbAOut_USB31XX(hid, channel, volts2, 0);

          auto current_time = std::chrono::high_resolution_clock::now();
          auto diff = std::chrono::duration_cast<std::chrono::microseconds>(current_time - start_time).count();
          if ((dt-diff)>0){

          usleep(dt-diff);
          }else{
          	usleep(dt);
          }
          //std::cout << "Program has been running for " << dt-diff << " microseconds" << std::endl;
	     
	    }
    	gettimeofday(&end1, NULL);
    	seconds  = end1.tv_sec  - start1.tv_sec;
    	useconds = end1.tv_usec - start1.tv_usec;

    	mtime = seconds + useconds/1000000.0;

    	printf("Elapsed time: %5.6f seconds\n", mtime);
    break;
    case 'a':
      printf("Testing the analog output for a single channel.\n");
      printf("Enter channel [0-15]: ");
      scanf("%d", &temp_channel);
      channel = (uint8_t) temp_channel;
      printf("Enter a range: 0 = 0-10V, 1 = +/- 10V, 2 = 0-20mA ");
      scanf("%d", &temp_range);
      range = (uint8_t) temp_range;
      printf("Enter a voltage: ");
      scanf("%f", &temp_volts);
      value = volts_USB31XX(range, temp_volts);
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
    case 'r':
      printf("\n Resetting DAQ Channels to 0 Volts.\n");
      range = (uint8_t) 0; // 0 = 0-10V, 1 = +/- 10V  2 = 0-20 mA
	  channel = (uint8_t) 0; // channel on DAQ for analog voltage output 0 - 15
      volts = 0;
      value = volts_USB31XX(range, volts);
      usbAOutConfig_USB31XX(hid, channel, range);
      usbAOut_USB31XX(hid, channel, value, 0);

      channel = (uint8_t) 2; // channel on DAQ for analog voltage output 0 - 15
      usbAOutConfig_USB31XX(hid, channel, range);
      usbAOut_USB31XX(hid, channel, value, 0);

      usbDConfigPort_USB31XX(hid, DIO_DIR_OUT);
	  usbDBitOut_USB31XX(hid, dpinx, volts);
	  usbDBitOut_USB31XX(hid, dpinz, volts);
	  break;
    case 'e':
      hid_close(hid);
      hid_exit();
      return 0;
      break;
    }
  }

  
  return 0;
}
