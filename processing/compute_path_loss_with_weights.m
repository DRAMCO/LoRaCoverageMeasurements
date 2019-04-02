
function [PL0_ols, n_ols, sigma_ols, PL0_ml, n_ml, sigma_ml, PL0_est, n_est, sigma_est] = compute_path_loss_with_weights(file)
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


    %Ordinary Least Squares (OLS) 
    a_est = inv(xt'*xt)*xt'*yt(find(t));
    sigma2_est = var(yt(find(t))-xt*a_est);

    PL0_ols = a_est(1);
    n_ols = a_est(2);
    sigma_ols = sqrt(sigma2_est);

    %Maximum likelihood (ML) estimates
    thetahat=censoredml(d, yt,c,t,a_est,sigma2_est)

    PL0_ml = thetahat(1);
    n_ml = thetahat(2);
    sigma_ml = thetahat(3);


    %Maximum likelihood (ML) estimates
    pars = censoredml_with_weights(d,yt,c,t,PL0_ols,n_ols,sigma_ols)
    PL0_est= pars(1);
    n_est = pars(2);
    sigma_est = pars(3);

    %S=['PL(d0)';'n';'sigma'];
    disp('   Estimate    OLS     ML         ML weight');
    fprintf('   PL(d0)      %.2f   %.2f     %.2f        \n', PL0_ols, PL0_ml, PL0_est)
    fprintf('   n           %.3f   %.3f     %.3f        \n', n_ols, n_ml, n_est)
    fprintf('   sigma       %.3f   %.3f     %.3f       \n',  sigma_ols, sigma_ml, sigma_est)
    disp('   ---------------------------------');
end