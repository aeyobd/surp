

We thank the referee for their detailed review and comments on our manuscript. We believe that the updates that we have made in response have improved its quality. We detail our specific changes and respond to each of the referee's comments below. 

### 1. General comments

> Overall, the manuscript is excessively long and, at times, confusing. . . . Moreover, the main conclusions are not particularly novel, as similar results have already been reported in previous studies (e.g. Romano et al. 2020). 

To shorten the paper and improve clarity, we moved Sections 6 and 7 to an Appendix. Instead, we retain a simplified version of Fig. 9 with a brief discussion in Section 5. We have also combined Figs. 1 and 2. These changes have shortened the main text from 14 to 11 pages. We also point out that Romano et al. (2020) actually state in their abstract that a more rigorous investigation of carbon production is needed. While the literature indeed already features investigations of C yields, these results are conflicting.

### 2. Choice of abundance diagnostics

> The rationale for adopting the [C/Mg] vs. [Mg/H] and [C/Mg] vs. [Mg/Fe] relations as primary diagnostics is unclear. The origin of a chemical element should be interpreted within the framework of the time-delay model. In this context, the [X/Fe] vs. [Fe/H] relation (where X = C or any other element) is the most informative diagnostic, as it directly reveals whether X is produced on the same timescales as Fe, and therefore by the same stellar sources.
> Approximately 70% of Fe is produced by Type Ia supernovae, with the remaining ~30% originating from core-collapse supernovae (CCSNe). If carbon were mainly produced on the same timescales as Fe, the [C/Fe] vs. [Fe/H] relation would be flat and solar. Conversely, if CCSNe dominate carbon production, one would expect [C/Fe] > 0 at low metallicity ([Fe/H] < −1), as observed for α-elements. Recent observations indeed indicate that [C/Fe] is enhanced at low metallicity, favoring massive stars as the primary carbon producers. This result is not new.
> It is therefore puzzling that the authors do not present or discuss the [C/Fe] ratio, instead focusing on less intuitive diagnostics such as [C/Mg] vs. [Mg/Fe], whose physical interpretation is not explained. It is unclear what additional information can be extracted from these diagrams.
> Furthermore, the manuscript does not mention that Mg yields from massive stars in the literature are highly uncertain and generally underestimated, requiring empirical corrections. This issue directly affects any analysis based on [C/Mg].
> While an increase of [C/Mg] with [Mg/H] is expected if AGB stars contribute to carbon production (as is well established), it is unclear what novel insight is gained by adopting the [C/Mg] ratio. The authors should clarify the motivation and added value of this choice.

We have added further justification of our chosen yield ratios to the text (in Sections 2 and 5.1) and a new single-panel figure (Fig. 6) with a short discussion on the utility of the [C/Fe]-[Fe/H] trend (new Section 5.3). 

Using [C/Mg] with both [Mg/Fe] and [Fe/H] is necessary to support our argument. By using [C/Mg] with [Mg/Fe], we implicitly study the [C/Fe] abundance trend. Within a time-delay framework, primary elements produced by delayed sources behave similarly to secondary elements produced in CCSN. A flat [C/Fe] trend with [Fe/H] may indicate either a substantial AGB production of C or a CCSN yield of C that increases with metallicity. This degeneracy is a justification that the Romano (2022) review provides for the lack of consensus on the origin of C.  

Regarding the uncertainties in Mg yields, we have added a short discussion to Section 4. We simply adopt metallicity-independent yields for Mg and O, so the uncertainties in the details of Mg production play a small role in our conclusions. 

### 3. Massive-star yields

> The authors adopt equation (9) to describe the metallicity dependence of carbon yields from massive stars, but its physical meaning and justification are not clearly explained. Why was this specific functional form chosen? Does it accurately reproduce the yields of Limongi & Chieffi (2018)? Additionally, the impact of stellar rotation on the yields, which is known to be significant, should be discussed.
>

We thank the referee for pointing out the unclear justification of Eq. 9. We have clarified Section 3.2 to better highlight that Eq. 9 was chosen for its simplicity and ability to approximate relevant features of CCSN yields. 

Our functional form reasonably reproduces the yields of most CCSN yields in the updated Fig. 3 near solar metallicity (including Limongi & Chieffi’s 2018 rotating yield models). We select a linear equation with metallicity also because of its simplicity. The linear form neatly represents a metallicity-independent component (primary carbon production) and production proportional to metallicity (secondary carbon production). This assumption is at least accurate enough to estimate $f_\text{agb}$, but more complex models may more accurately represent observed trends and theoretical models. These variations do not significantly alter our results

### 4. Stellar lifetimes

> In Section 3.1, the authors adopt the main-sequence mass–lifetime relation from Larson (1974). This choice is outdated, and more modern prescriptions exist that are consistent with the stellar yields adopted in the paper. A justification for using such an old relation is required.
>

It is true that Larson (1974) is an older model for the mass–lifetime relation. We have added a sentence in Section 3.1 discussing this choice. Our model depends most directly on the lifetimes of  stars with initial masses between 1 and 8 $\mathrm{M}_\odot$ since those stars undergo a C-producing AGB phase. More recent mass-lifetime relations do not substantially alter lifetimes in this mass range, so we find they do not change our results significantly (see appendix A in J. W. Johnson et al. 2023).

### 5. Chemical evolution model assumptions

> It is unclear whether the chemical evolution model includes gas infall to form the MW disk. The description suggests that only galactic winds may be included. If this is the case, it would be inconsistent with standard MW chemical evolution models. The assumptions regarding infall and outflows should be clearly and explicitly stated.
>

Our model does indeed include gas infall, consistent with current GCE models. We have adjusted Section 4 to more explicitly state our model assumptions regarding inflows and outflows. 

### 6. Type Ia supernova delay-time distribution

> The adopted delay-time distribution (DTD) function for Type Ia SNe follows a t⁻¹·¹ dependence, which is reasonable. However, the assumed minimum explosion time of 150 Myr is too long and neglects the existence of prompt Type Ia SNe with delay times shorter than 100 Myr, which are observationally supported, particularly in regions of active star formation (e.g. Mannucci et al. 2006).
> Standard progenitor models for Type Ia SNe involve C–O white dwarfs originating from progenitors with masses up to 8–9 M⊙, implying a minimum delay time of ~30 Myr (Greggio 2005). The most successful chemical evolution models, which reproduce observed abundance patterns and cosmic Type Ia SN rate, include approximately 10% prompt Type Ia SNe (e.g. Palicio et al. 2024). While this issue may not significantly alter the main results, adopting an unrealistically long minimum delay time risks propagating an incorrect assumption. The value of 150 Myr originates from empirical studies of the cosmic Type Ia SN rate, which remains highly uncertain.

We have updated the Type Ia SNe delay-time distribution, reducing the minimum delay time to 40 Myr and adopting the time-dependence recommended by Dubay et al. (2024). With similar GCE models, Dubay et al. (2024) find that an approximation of Greggio's (2005) WIDE DD model best matches the [$\alpha$/Fe]-[Fe/H] APOGEE trends. While changing the Type Ia SN DTD affects our results, we find that the updates are principally dependent on the time-integrated delayed SN Ia yield of Fe rather than the detailed time dependence. Our new models favour a slightly higher AGB contribution but leave our qualitative results similar.

### 7. Bursting star formation mode

> Section 5.5 explores a bursting mode of star formation. However, the justification for adopting such a mode is unclear. As expected, no significant differences are found, since chemical abundances depend primarily on the time-integrated star formation rate rather than its detailed temporal structure. This result is well known, and the section could be significantly shortened.
>

We have moved models exploring variations in the star formation to the appendix to shorten the main text. We are glad the referee agrees that the SFH should have a minor role in Milky Way trends. However, many astronomers less versed in GCE often interpret all abundance trends in terms of SFH. We retain a comparison of different SFH models in the appendix for readers less familiar with GCE modelling. 

### 8. Dwarf galaxy model

>  Dwarf galaxies are characterized by lower star formation rates than the MW disk and by strong galactic winds, which are not observed in the MW. Why the MW model assumes galactic winds? In the MW galactic fountains are more likely than galactic winds. More information about the dwarf model would be welcome.
> Is the same IMF adopted for both systems? In addition, a plot of [O/Fe] vs. [Fe/H] for the dwarf galaxy should be provided to verify that [O/Fe] declines more steeply than in the MW, as expected.

We have clarified the description of the dwarf galaxy model, and also moved the original Section 7 to an appendix.  

We have added a paragraph discussing the differences between Galactic winds and fountains for chemical evolution in Section 4. Whether a hydrodynamic simulation exhibits galactic fountains or gas outflows depends on the uncertain choice of stellar feedback model. However, our main conclusions are likely not dependent on the details of gas outflows versus galactic fountains. These prescriptions primarily affect the amount of H that mixes with newly produced metals (see, e.g., the analytic solutions in Johnson, 2025). 

Regarding the [O/Fe]-[Fe/H] evolution of our dwarf galaxy model, our parameters are chosen based on the best-fit values for GSE determined by Johnson et al. (2023b). Assuming a solar mixture of O and Mg, the model therefore reproduces the observed [O/Fe]-[Fe/H] evolution by construction. We omit a figure showing this evolution, since Johnson et al. (2023b) already presents detailed modelling of alpha and iron-peak element enrichment in GSE. We have added a reference to their fig. 5 in the new Appendix D. 