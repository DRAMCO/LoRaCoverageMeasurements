% CENSOREDVAR Computes the theoretical asymptotic variance for
% the estimates of the censored ML estimator.
%
%   CENSOREDVAR(X,C,PLd0,N,SIGMA) uses the equations from T. Amemiya,
%   "Regression Analysis when the dependent variable is truncated normal",
%   Econometrica, 1987. C is the censoring level, PLd0, N and SIGMA are
%   either true or estimated pathloss parameter values. If You use this 
%   code, or parts of it, please cite the following paper: 
%   C. Gustafson, T. Abbas, D. Bolin and F. Tufvesson,
%   "Statistical Modeling and Estimation of Censored Pathloss Data",
%   IEEE Wireless Communications Letters, 2015.
%
%   Copyright (C) 2015, David Bolin, Carl Gustafson.
%
%   This program is free software: you can redistribute it and/or modify
%   it under the terms of the GNU General Public License as published by
%   the Free Software Foundation, either version 3 of the License, or
%   (at your option) any later version.
%
%   This program is distributed in the hope that it will be useful,
%   but WITHOUT ANY WARRANTY; without even the implied warranty of
%   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
%   GNU General Public License for more details.
%
%   You should have received a copy of the GNU General Public License
%   along with this program.  If not, see <http://www.gnu.org/licenses/>.

function censvar=censoredvar(x,c,PLd0,n,sigma)

z=x*[-PLd0+c -n]'/sigma;
phi=normpdf(z);
Phi=normcdf(z);

zp = z.*phi;
r=2./(sqrt(2*pi)*erfcx(z/(sqrt(2))));
ai=-(zp-phi.*r-Phi)/sigma^2;
bi=(z.*zp+phi-zp.*r)/(2*sigma^3);
ci=-(z.^2.*zp+zp-z.*zp.*r-2*Phi)/(4*sigma^4);
bx  =sum(bsxfun(@times,bi,x));
censvar=(diag(inv([bsxfun(@times,ai,x)'*x bx'; bx sum(ci)])));
