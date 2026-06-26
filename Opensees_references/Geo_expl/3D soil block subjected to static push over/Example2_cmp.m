%test by Lei in July 2018
clear all
close all
clc

figure (1)
load disp3.out
load disp3a1.out
load disp3a2.out
load disp3a3.out

load ddm3G.out
param =60000;
plot(ddm3G(:,1),ddm3G(:,2),'r')
hold on
plot(ddm3G(:,1),(disp3a1(:,2)-disp3(:,2))/(0.1*param),'b--','linewidth',2)
plot(ddm3G(:,1),(disp3a2(:,2)-disp3(:,2))/(0.001*param),'g','linewidth',2)
plot(ddm3G(:,1),(disp3a3(:,2)-disp3(:,2))/(0.00001*param),'k','linewidth',2)


legend('DDM','FFD 0.01','FFD 0.001','FFD 0.00001')
xlabel('Time [sec]')
ylabel('\partialu_3/\partialG')
set(get(gca,'ylabel'),'Fontsize',14) 
set(get(gca,'xlabel'),'Fontsize',14) 
set(gca,'Fontsize',14) 


figure(2)
load ddm3k.out

load disp3K1.out
load disp3K2.out
load disp3K3.out
load disp3K4.out
param =2.4e5;
plot(ddm3k(:,1),ddm3k(:,2),'r')
hold on
plot(ddm3k(:,1),(disp3K1(:,2)-disp3(:,2))/(0.01*param),'b--','linewidth',2)
plot(ddm3k(:,1),(disp3K2(:,2)-disp3(:,2))/(0.001*param),'g','linewidth',2)
plot(ddm3k(:,1),(disp3K3(:,2)-disp3(:,2))/(0.0001*param),'k','linewidth',2)
plot(ddm3k(:,1),(disp3K4(:,2)-disp3(:,2))/(0.00001*param),'m:','linewidth',2)

legend('DDM','FFD 0.01','FFD 0.001','FFD 0.0001','FFD 0.00001')
xlabel('Time [sec]')
ylabel('\partialu_3/\partialK')
set(get(gca,'ylabel'),'Fontsize',14) 
set(get(gca,'xlabel'),'Fontsize',14) 
set(gca,'Fontsize',14) 

