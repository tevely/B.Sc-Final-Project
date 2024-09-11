function eps = epsKTPkato(wl, i)
% KTP Sellmeier dispersion equation used in according to [1]
%
% Reference
% [1] K. Kato and E. Takaoka, Appl. Opt., AO 41, 5040 (2002).
%
% INPUT:
% wl - wavelength [um]
% i - number of diagonal component (1, 2, 3)

A = [3.29100, 3.45018, 4.59423];
B1 = [0.04140, 0.04341, 0.06206];
C1 = [0.03978, 0.04597, 0.04763];
B2 = [9.35522, 16.98825, 110.80672];
C2 = [31.45571, 39.43799, 86.12171];
eps = A(i) + B1(i) ./ (wl.^2-C1(i))+B2(i)./(wl.^2-C2(i));
end
