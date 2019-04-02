function pars=censoredml_with_weights(d,y,c,t,PL0,n,sigma)

  opts = optimset('GradObj','off', 'Largescale','off','MaxFunEvals',20000,'MaxIter',20000);
  N = 30;
  [count,edges, bin] = histcounts(d,N);
  Nb = count(bin);
  Ns = numel(d);
  w = ((1./Nb).*(Ns./N))';
  x0 = [PL0;n;sigma];
  pars = fminsearch(@(pars) censoredllh(pars),x0,opts);

  function l = censoredllh(p)
    L = zeros(size(y));
    n = p(2);
    PL0 = p(1);
    sigma = p(3);

    PLm = 10*n*log10(d(t==1)') + PL0;
    PLm_star = 10*n*log10(d(t==0)') + PL0;

    L(t==1) = (-log(sigma) + log(normpdf((y(t==1)-PLm)./sigma)));
    L(t==0)=(log(1-normcdf((c-PLm_star)./sigma)));

    L = L.*w;
    l = -sum(L);
  end
end