clear all;
amplitude = 1.0;

update_rate = 50; % update current through coils at 10 Hz (20 times per second)
dt = 1/update_rate; % time between samples

cycle_length = 2*pi; % sine wave has a cycle length of 2pi

num_cycles = 1;
wave_freq = 2; % sine wave frequency is 1 Hz = 1 cycle / sec

total_time = 1; %1 second; final time for 1 cycle/ 1 waveform.

num_samples = update_rate
% Need to scale sine wave such that 1 sine wave cycle will fit into the
% update rate of the coils (10 samples)
time = 0:1/update_rate:1;
num_iter = update_rate * total_time;
for i = 1:update_rate+1

%   % Multiply by 2*pi--now it's one cycle per sample:
    buffer(i) = amplitude * sin(wave_freq*(2 * pi) * time(i)); 
%    
%   % Multiply by 1 samples per second--now it's 1 cycles per second:
   buffer2(i) = amplitude * sin(wave_freq * (2*pi) *time(i) - pi/2);
  % Divide by 10 samples per second--now it's 1 cycles per 1 samples, which is just what we needed:
%     buffer(i) = amplitude * sin(wave_freq * (2 * pi) * i / update_rate);
end


xval = 1:num_samples;
figure(1);clf;
plot(time,buffer,'-*b','MarkerSize',12,'LineWidth',2);hold on;
plot(time,buffer2,'-*r','MarkerSize',12,'LineWidth',2);
plot(time,buffer+buffer2,'-*g','MarkerSize',12,'LineWidth',2);
legend('sine','pi/2 lag sine','sum')

