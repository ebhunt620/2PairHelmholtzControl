clear all;
amplitude = 1.0;

update_rate = 100; % update current through coils at 10 Hz (20 times per second)
dt = 1/update_rate; % time between samples

cycle_length = 2*pi; % sine wave has a cycle length of 2pi

wave_freq = 1; % sine wave frequency is 1 Hz = 1 cycle / sec

num_cycles = 1; %1 second; final time for 1 cycle/ 1 waveform.

% Need to scale sine wave such that 1 sine wave cycle will fit into the
% update rate of the coils (10 samples)
time = 0:1/update_rate:num_cycles;
num_iter = update_rate * num_cycles;
for i = 1:(update_rate * num_cycles)+1

%   % Multiply by 2*pi--now it'sone cycle per sample:
    buffer(i) = amplitude * sin(wave_freq*(2 * pi) * time(i)); 
%    
%   % Multiply by 1 samples per second--now it's 1 cycles per second:
   buffer2(i) = amplitude * sin(wave_freq * (2*pi) *time(i) - pi/2);
  % Divide by 10 samples per second--now it's 1 cycles per 1 samples, which is just what we needed:
%     buffer(i) = amplitude * sin(wave_freq * (2 * pi) * i / update_rate);
end

figure(1);clf;
for k = 1:size(buffer,2)
    plot(time(k),buffer(k),'-*b','MarkerSize',12,'LineWidth',2);hold on;
    plot(time(k),buffer2(k),'-*r','MarkerSize',12,'LineWidth',2);
    plot(time(k),buffer(k)+buffer2(k),'-*g','MarkerSize',12,'LineWidth',2);
    pause(dt)
end
plot(time,buffer,'-*b','MarkerSize',12,'LineWidth',2);hold on;
plot(time,buffer2,'-*r','MarkerSize',12,'LineWidth',2);
plot(time,buffer+buffer2,'-*g','MarkerSize',12,'LineWidth',2);
legend('Z Coil: sine','X Coil: pi/2 lag sine','sum')
hold off;
% Reverse sine wave for backward swimming

for i = 1:(update_rate * num_cycles)+1

%   % Multiply by 2*pi--now it'sone cycle per sample:
    buffer_bkwd(i) = amplitude * sin(wave_freq*(2 * pi) * time(i)); 
%    
%   % Multiply by 1 samples per second--now it's 1 cycles per second:
   buffer2_bkwd(i) = amplitude * sin(wave_freq * (2*pi) *time(i) -3*pi/2);
  % Divide by 10 samples per second--now it's 1 cycles per 1 samples, which is just what we needed:
%     buffer(i) = amplitude * sin(wave_freq * (2 * pi) * i / update_rate);
end


figure(2);clf;
for k = 1:size(buffer,2)
    plot(time(k),buffer_bkwd(k),'-*b','MarkerSize',12,'LineWidth',2);hold on;
    plot(time(k),buffer2_bkwd(k),'-*r','MarkerSize',12,'LineWidth',2);
    plot(time(k),buffer_bkwd(k)+buffer2_bkwd(k),'-*g','MarkerSize',12,'LineWidth',2);
    pause(dt)
end
plot(time,buffer_bkwd,'-*b','MarkerSize',12,'LineWidth',2);hold on;
plot(time,buffer2_bkwd,'-*r','MarkerSize',12,'LineWidth',2);
plot(time,buffer_bkwd+buffer2_bkwd,'-*g','MarkerSize',12,'LineWidth',2);
legend('sine','pi/2 lag sine','sum')




