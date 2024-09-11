figure
hold on
wls = linspace(0.3,3,300);
for i=1:3
    plot(wls,sqrt(epsKTPkato(wls,crystal_axes(i))))
    title("KTP dispersion (Kato and Takaoka 2002)")
    xlabel("Wavelength [um]")
    ylabel("Refractive indices")
end