function pars=censoredml_with_var_sigma(d,y,c,t,PL0,n,a,b)

  opts = optimset('GradObj','off', 'Largescale','off','MaxFunEvals',20000,'MaxIter',20000);
  x0 = [PL0;n;a;b];
  pars = fminsearch(@(pars) censoredllh(pars),x0,opts);
  
  function l = censoredllh(p)
    L = zeros(size(y));
    n = p(2);
    PL0 = p(1);
    a = p(3);
    b = p(4);
    
    sigma = a * log10(d(t==1)') + b;
    sigma_star = a * log10(d(t==0)') + b;
    
    PLm = 10*n*log10(d(t==1)') + PL0;
    PLm_star = 10*n*log10(d(t==0)') + PL0;
    
    L(t==1) = -log(sigma) + log(normpdf((y(t==1)-PLm)./sigma));
    
    L(t==0)=log(1-normcdf((c-PLm_star)./sigma_star));
    l = -sum(L);
  end
end