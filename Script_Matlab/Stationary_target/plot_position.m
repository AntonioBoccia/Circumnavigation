%% PLOT COUNTERCLOCKWISE ANGLES
figure(1)
%title('Counterclocwise angles')
plot(y1_x,y1_y,'b')
hold on
plot(y2_x,y2_y,'r')
hold on
plot(y3_x,y3_y,'g')
hold on
plot(y4_x,y4_y,'k')
hold on
plot(y5_x,y5_y,'m')
grid on
xlabel('y_{i1}');
ylabel('y_{i2}');
legend('y_1(t)','y_2(t)','y_3(t)','y_4(t)','y_5(t)');
axis('equal')

hold on
plot(y1_x(end),y1_y(end),'o-k','LineWidth',2);
hold on 
plot(y3_x(end),y3_y(end),'o-k','LineWidth',2);
hold on
plot(y4_x(end),y4_y(end),'o-k','LineWidth',2);
hold on
plot(y5_x(end),y5_y(end),'o-k','LineWidth',2);
hold on
