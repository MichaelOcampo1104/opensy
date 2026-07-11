%%
clear;
clc;
%% simulation flag
flag_simu = 1;
%% read hinge calibration data
df = importdata('./hinge_calibration_examples.csv');
% read in data
cali.test_id = df.textdata(2:end,2);
cali.beam_type = df.data(:,1);
cali.b = df.data(:,2);
cali.h = df.data(:,3);
cali.ln = df.data(:,4);
cali.fc = df.data(:,5);
cali.V = df.data(:,[6:2:14]);
cali.theta = df.data(:,[7:2:15]);
cali.px = df.data(:,16);
cali.py = df.data(:,17);
cali.beta = df.data(:,18);
cali.rnp = df.data(:,19);
cali.rpp = df.data(:,20);
cali.wind_step = df.data(:,21);
cali.num_test = length(cali.test_id);
cali.EcIg = 57.0*sqrt(cali.fc*1000).*(1/12*cali.b.*cali.h.^3);
cali.Ke = cali.EcIg*12./(cali.ln.^3);
%% load test data
dir_td = './TestData/';
for id = 1:1:cali.num_test
    res = importdata([dir_td,cali.test_id{id,1},'.txt']);
    test.hinge_shear{id,1} = res(:,2);
    test.hinge_disp{id,1} = res(:,1);
    test.hinge_rot{id,1} = res(:,1)/cali.ln(id);
end
%% write hinge modeling parameters into tcl files
dir_mp = './ModelingParameters/';
for id = 1:1:cali.num_test
    cur_filename = [dir_mp,cali.test_id{id,1},'.tcl'];
    cur_file = fopen(cur_filename,'w');
    fprintf(cur_file,'set b %6.2f;\n',cali.b(id));
    fprintf(cur_file,'set h %6.2f;\n',cali.h(id));
    fprintf(cur_file,'set L %6.2f;\n',cali.ln(id));
    fprintf(cur_file,'set fc %6.2f;\n',cali.fc(id));
    for i = 1:1:5
        fprintf(cur_file,'set V%d %6.2f;\n',i,cali.V(id,i));
        fprintf(cur_file,'set theta%d %12.9f;\n',i,cali.theta(id,i));
    end
    fprintf(cur_file,'set px %6.2f;\n',cali.px(id));
    fprintf(cur_file,'set py %6.2f;\n',cali.py(id));
    fprintf(cur_file,'set beta %6.2f;\n',cali.beta(id));
    fprintf(cur_file,'set rnp %6.2f;\n',cali.rnp(id));
    fprintf(cur_file,'set rpp %6.2f;\n',cali.rpp(id));
    fclose(cur_file);
end
%% run simulations and load results
run_list = [1:1:cali.num_test];
dir_sm = './SimuOutput/';
for idx = 1:1:length(run_list)
    id = run_list(idx);
    % set the model id
    cur_filename = './model_id.tcl';
    cur_file = fopen(cur_filename,'w');
    fprintf(cur_file,'set model_id %s;\n',cali.test_id{id,1});
    fclose(cur_file);
    % run
    if flag_simu
        ! OpenSees run_simulation.tcl
    end
    % read results
    res = importdata([dir_sm,cali.test_id{id,1},'/disp.out']);
    simu.hinge_shear{id,1} = res(:,1);
    simu.hinge_disp{id,1} = res(:,2);
    simu.hinge_rot{id,1} = res(:,2)/cali.ln(id);
end
%% stiffness
for idx = 1:1:length(run_list)
    id = run_list(idx);
    if cali.wind_step(id)<0
        lp_tag = length(test.hinge_rot{id,1});
        lp_tag2 = length(test.hinge_rot{id,1});
    else
        lp_tag = min(length(test.hinge_rot{id,1}),cali.wind_step(id));
        lp_tag2 = cali.wind_step(id);
    end
    if (find([11]==id))
        skip_tol = 5;
    %elseif (find([18:1:24]==id))
    elseif cali.wind_step(id)>0
        skip_tol = -1;
    else
        skip_tol = 2;
    end
    [test.kscec{id,1}, test.peak_forces{id,1}, test.peak_disp{id,1}] = secant_stiffness(test.hinge_disp{id,1}(1:lp_tag),test.hinge_shear{id,1}(1:lp_tag),-1,skip_tol);
    [simu.kscec{id,1}, simu.peak_forces{id,1}, simu.peak_disp{id,1}] = secant_stiffness(simu.hinge_disp{id,1}(1:lp_tag2),simu.hinge_shear{id,1}(1:lp_tag2),-1,skip_tol);
    if cali.wind_step(id)>0
        [test.kscec{id,2}, test.peak_forces{id,2}, test.peak_disp{id,2}] = secant_stiffness(test.hinge_disp{id,1}(lp_tag+1:end),test.hinge_shear{id,1}(lp_tag+1:end),-1,skip_tol);
        [simu.kscec{id,2}, simu.peak_forces{id,2}, simu.peak_disp{id,2}] = secant_stiffness(simu.hinge_disp{id,1}(lp_tag2+1:end),simu.hinge_shear{id,1}(lp_tag2+1:end),-1,skip_tol);
    end
end
%% plot
dir_res = './FigOutput/';
for idx = 1:1:length(run_list)
    id = run_list(idx);
    if cali.wind_step(id)<0
        lp_tag = length(test.hinge_rot{id,1});
        lp_tag2 = length(test.hinge_rot{id,1});
    else
        lp_tag = min(length(test.hinge_rot{id,1}),cali.wind_step(id));
        lp_tag2 = cali.wind_step(id);
    end
    f1 = figure;
    set(f1, 'Units', 'inches', 'Position', [1, 1, 9, 4]);
    subplot(1,2,1);
    p1 = plot(test.hinge_rot{id,1}(1:lp_tag),test.hinge_shear{id,1}(1:lp_tag),'-k','linewidth',1.5);
    hold on;
    p2 = plot(simu.hinge_rot{id,1}(1:lp_tag2),simu.hinge_shear{id,1}(1:lp_tag2),'--','color',[0.5,0.5,0.5],'linewidth',1.5);
    xlabel('Chord rotation (in/in)');
    ylabel('Shear (kip)');
    legend([p1;p2],{'Test';'Simulation'},'Location','northwest');
    set(gca,'fontname','Gill Sans MT','FontSize',14);
    grid on;
    subplot(1,2,2);
    p1 = plot(test.kscec{id,1}/cali.Ke(id),'-ok','markersize',2,'linewidth',1.5);
    hold on;
    p2 = plot(simu.kscec{id,1}/cali.Ke(id),'--o','markersize',2,'color',[0.5,0.5,0.5],'linewidth',1.5);
    xlabel('Cycle number');
    ylabel('I_{sec}/I_{g}');
    legend([p1;p2],{'Test';'Simulation'});
    set(gca,'fontname','Gill Sans MT','FontSize',14);
    grid on;
    savefig(f1,[dir_res,cali.test_id{id,1},'_1.fig']);
    exportgraphics(f1, [dir_res,cali.test_id{id,1},'_1.png'], 'Resolution', 600);
    close(f1);
    if cali.wind_step(id)>0
        f1 = figure;
        set(f1, 'Units', 'inches', 'Position', [1, 1, 9, 4]);
        subplot(1,2,1);
        p1 = plot(test.hinge_rot{id,1}(lp_tag+1:end),test.hinge_shear{id,1}(lp_tag+1:end),'-k','linewidth',1.5);
        hold on;
        p2 = plot(simu.hinge_rot{id,1}(lp_tag2+1:end),simu.hinge_shear{id,1}(lp_tag2+1:end),'--','color',[0.5,0.5,0.5],'linewidth',1.5);
        xlabel('Chord rotation (in/in)');
        ylabel('Shear (kip)');
        legend([p1;p2],{'Test';'Simulation'},'Location','northwest');
        set(gca,'fontname','Gill Sans MT','FontSize',14);
        grid on;
        subplot(1,2,2);
        p1 = plot(test.kscec{id,2}/cali.Ke(id),'-ok','markersize',2,'linewidth',1.5);
        hold on;
        p2 = plot(simu.kscec{id,2}/cali.Ke(id),'--o','markersize',2,'color',[0.5,0.5,0.5],'linewidth',1.5);
        xlabel('Cycle number');
        ylabel('I_{sec}/I_{g}');
        legend([p1;p2],{'Test';'Simulation'});
        set(gca,'fontname','Gill Sans MT','FontSize',14);
        grid on;
        savefig(f1,[dir_res,cali.test_id{id,1},'_2.fig']);
        exportgraphics(f1, [dir_res,cali.test_id{id,1},'_2.png'], 'Resolution', 600);
        close(f1);
    end
end

%%
function [ksec,peak_forces,peak_disp] = secant_stiffness(disp, forc, plot_flag,skip_tol)
    % determine cycles by passing zero displacement
    disp_sign = disp>0;
    disp_pass_zero = diff(disp_sign)~=0;
    idx_pass_zero = find(disp_pass_zero>0);
    idx_pass_zero = [idx_pass_zero;length(disp)];
    rm_tag = [];
    for ix = 1:1:length(idx_pass_zero)-1
        if abs(idx_pass_zero(ix)-idx_pass_zero(ix+1))<skip_tol
            rm_tag = [rm_tag;ix];
        end
    end
    idx_pass_zero(rm_tag) = [];
    if idx_pass_zero(1) ~= 1
        idx_pass_zero = [1;idx_pass_zero];
    end
    % plot to check
    if plot_flag > 0
        figure;
        plot(disp,'-k');
        hold on;
        plot(idx_pass_zero,disp(idx_pass_zero),'ob');
        grid on;
        xlabel('Load step');
        ylabel('Lateral displacement/rotation');
        legend('Raw data','Pass zero');
    end
    
    %% find peaks
    % each interval between two passing zero contains one peak
    loc = [];
    pks = [];
    %sign = 1; % if first peak is positive: 1, otherwise: -1
    if length(idx_pass_zero) > 1
        cursign = sign(mean(disp(idx_pass_zero(1):idx_pass_zero(2))));
    else
        cursign = 1;
    end
    for i = 1:1:length(idx_pass_zero)-1
        cur_cycle = disp(idx_pass_zero(i):idx_pass_zero(i+1))*cursign;
        [tmp_pks, tmp_loc] = max(cur_cycle);
        cur_pks = tmp_pks;
        cur_loc = idx_pass_zero(i)+tmp_loc-1;
        pks = [pks; cur_pks*cursign];
        loc = [loc; cur_loc];
        % swarp sign
        cursign = -cursign;
    end
    % plot to check
    if plot_flag > 0
        figure;
        plot(disp,'-k');
        hold on;
        plot(loc,pks,'or');
        grid on;
        xlabel('Load step');
        ylabel('Lateral displacement/rotation');
        legend('Raw data','Peaks');
    end
    % Displaying peak values for Test
    peak_forces = [];
    peak_disp = [];
    for i = 1:length(loc)
        peak_forces = [peak_forces; forc(loc(i))];
        peak_disp = [peak_disp;disp(loc(i))];
    end
    %% secant stiffness
    forc = forc(loc);
    ksec = [];
    for cur_idx = 1:1:length(pks)
        if pks(cur_idx) > 0
            if cur_idx == 1
                cur_neg = [0, 0];
            else
                cur_neg = [pks(cur_idx-1), forc(cur_idx-1)];
            end
            cur_pos = [pks(cur_idx), forc(cur_idx)];
        else
            continue;
            if cur_idx == 1
                cur_pos = [0, 0];
            else
                cur_pos = [pks(cur_idx-1), forc(cur_idx-1)];
            end
            cur_neg = [pks(cur_idx), forc(cur_idx)];
        end
        cur_ksec = (cur_pos(2)-cur_neg(2))/(cur_pos(1)-cur_neg(1));
        ksec = [ksec; cur_ksec];
    end
    % plot to check
    if plot_flag > 0
        figure;
        plot(ksec,'-ok','MarkerSize',2);
        grid on;
        xlabel('Cycle');
        ylabel('Secant stiffness');
    end
    % 
    if length(ksec) < 1
        ksec = [0];
    end
end
