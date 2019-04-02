
function [a_est, sigma_est, thetahat, sqrt_Avarhat] = compute_path_loss_with_weights(file)
    load(file)
    y = y';
    c = double(c);
    
    %Define indicator for censore and uncensored samples
    t(find(y<c))=1;
    t(find(y>=c))=0;

    %Censoring of the synthetic data
    yt=zeros(length(y),1);
    yt(find(y<c))=y(find(y<c));
    yt(find(y>=c))=c;
    xt=x(find(y<c),:);

    sigmas2_est = zeros(length(y),1);

    %Ordinary Least Squares (OLS) 
    a_est = inv(xt'*xt)*xt'*yt(find(t));
    sigma2_est = var(yt(find(t))-xt*a_est);

    %Maximum likelihood (ML) estimates
    thetahat=censoredml(x,yt,c,t,a_est,sigmas2_est+sigma2_est)

    %Asymptotic variance
    Avarhat=censoredvar(x,c,thetahat(1),thetahat(2),thetahat(3));
    %S=['PL(d0)';'n';'sigma'];
    disp('   Estimate    OLS     ML    | True value');
    disp(sprintf('   PL(d0)      %.2f   %.2f ', a_est(1), thetahat(1)))
    disp(sprintf('   n           %.3f   %.3f ', a_est(2), thetahat(2)))
    disp(sprintf('   sigma       %.3f   %.3f ', sqrt(sigma2_est), thetahat(3)))
    disp('   ---------------------------------');
    disp('   Asymptotic standard errors (SE) of ML estimates');
    disp('                 SE(true value) SE(estimated value)');
    disp(sprintf('   SE(PL(d0))    %.2f           ', sqrt(Avarhat(1))))
    disp(sprintf('   SE(n)         %.3f        ',  sqrt(Avarhat(2))))
    disp(sprintf('   SE(sigma^2)   %.3f       ',  sqrt(Avarhat(3))))
    
    sigma_est = sqrt(sigma2_est);
    sqrt_Avarhat = sqrt(Avarhat);
end