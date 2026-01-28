Thank you for your detailed review and comments on this draft. We hope that the updated draft better clarifies the details of the model and justifies the assumptions you are concerned about. 

In general, it is true that some previous studies have reached similar conclusions. We note that results in the literature have, however, remained conflicting  and mostly qualitative. For example, Romano et al. (2020) test a total of only 4 yield sets and acknowledge in their abstract that a more rigorous investigation of carbon is needed (also discussed in the Romano 2022 review).



1. Choice of abundance diagnostics

*The rationale for adopting the [C/Mg] vs. [Mg/H] and [C/Mg] vs. [Mg/Fe] relations as primary diagnostics is unclear. The origin of a chemical element should be interpreted within the framework of the time-delay model. In this context, the [X/Fe] vs. [Fe/H] relation (where X = C or any other element) is the most informative diagnostic, as it directly reveals whether X is produced on the same timescales as Fe, and therefore by the same stellar sources.*
*Approximately 70% of Fe is produced by Type Ia supernovae, with the remaining ~30% originating from core-collapse supernovae (CCSNe). If carbon were mainly produced on the same timescales as Fe, the [C/Fe] vs. [Fe/H] relation would be flat and solar. Conversely, if CCSNe dominate carbon production, one would expect [C/Fe] > 0 at low metallicity ([Fe/H] < −1), as observed for α-elements. Recent observations indeed indicate that [C/Fe] is enhanced at low metallicity, favoring massive stars as the primary carbon producers. This result is not new.*
*It is therefore puzzling that the authors do not present or discuss the [C/Fe] ratio, instead focusing on less intuitive diagnostics such as [C/Mg] vs. [Mg/Fe], whose physical interpretation is not explained. It is unclear what additional information can be extracted from these diagrams.*
*Furthermore, the manuscript does not mention that Mg yields from massive stars in the literature are highly uncertain and generally underestimated, requiring empirical corrections. This issue directly affects any analysis based on [C/Mg].*
*While an increase of [C/Mg] with [Mg/H] is expected if AGB stars contribute to carbon production (as is well established), it is unclear what novel insight is gained by adopting the [C/Mg] ratio. The authors should clarify the motivation and added value of this choice.*

Thank you for pointing out that we do not properly introduce our chosen abundance ratios. We have added further justification to our chosen yield ratios to the text and a short discussion on the [C/Fe]-[Fe/H] trend. 

However, we disagree that [C/Fe] with [Fe/H] alone is informative as to C's origin. In particular, a number of theoretical and observational works suggest that C production by massive stars may be strongly metallicity-dependent, especially in the case of rotating stars (as you also mention). As a result, a flat [C/Fe] ratio with metallicity may instead indicate that CCSNe C production increases with metallicity. Using the [C/Fe] versus [Fe/H] to ascertain the origin of C risks confounding metallicity dependence with the C source, something most previous studies often did not attempt to address. Within a time-delay framework, primary elements produced by delayed sources behave similarly to secondary elements produced in CCSN. This degeneracy is a justification the Romano (2022) review provides for the lack of consensus on the origin of C. For illustration, we have included a new figure (in appendix C) which shows how [C/Fe]-[Fe/H] is not more informative than [C/Mg]-[Mg/H].



2. Massive-star yields

The authors adopt equation (9) to describe the metallicity dependence of carbon yields from massive stars, but its physical meaning and justification are not clearly explained. Why was this specific functional form chosen? Does it accurately reproduce the yields of Limongi & Chieffi (2018)? Additionally, the impact of stellar rotation on the yields, which is known to be significant, should be discussed.

Thank you for mentioning that equation 9 appears to be insufficiently justified. We have clarified this section to better highlight that equation 9 was chosen for its simplicity and ability to approximate CCSNe C production including Limongi & Chieffi (2018).

3. Stellar lifetimes

*In Section 3.1, the authors adopt the main-sequence mass–lifetime relation from Larson (1974). This choice is outdated, and more modern prescriptions exist that are consistent with the stellar yields adopted in the paper. A justification for using such an old relation is required.*

Yes it is true that Larson (1974) is an older model for the mass–lifetime relation. We have added a sentence in the text justifying this choice. As additional background, many mass–lifetime relations (e.g., including Vincenzo et al. 2016) similar for stars with initial masses between 1 and 10 solar masses (see appendix A in Johnson, J. W. et al. 2023). Our model only depends on the mass–lifetime relation for AGB enrichment, so other choices should not affect the model. 

4. Chemical evolution model assumptions

*It is unclear whether the chemical evolution model includes gas infall to form the MW disk. The description suggests that only galactic winds may be included. If this is the case, it would be inconsistent with standard MW chemical evolution models. The assumptions regarding infall and outflows should be clearly and explicitly stated.*

We appreciate that you mention this lack of clarity. Our choice of infall and outflows are more explicitly stated in the revised draft. 

5. Type Ia supernova delay-time distribution

*The adopted delay-time distribution (DTD) function for Type Ia SNe follows a t⁻¹·¹ dependence, which is reasonable. However, the assumed minimum explosion time of 150 Myr is too long and neglects the existence of prompt Type Ia SNe with delay times shorter than 100 Myr, which are observationally supported, particularly in regions of active star formation (e.g. Mannucci et al. 2006).*
*Standard progenitor models for Type Ia SNe involve C–O white dwarfs originating from progenitors with masses up to 8–9 M⊙, implying a minimum delay time of ~30 Myr (Greggio 2005). The most successful chemical evolution models, which reproduce observed abundance patterns and cosmic Type Ia SN rate, include approximately 10% prompt Type Ia SNe (e.g. Palicio et al. 2024). While this issue may not significantly alter the main results, adopting an unrealistically long minimum delay time risks propagating an incorrect assumption. The value of 150 Myr originates from empirical studies of the cosmic Type Ia SN rate, which remains highly uncertain.*

Thank you for pointing out this limitation of the model. As we have ran model with a shorter Type Ia SNe minimum delay time of 30 Myr and derive similar results, we have added a sentence acknowledging that the minimum delay time may be shorter than we adopt.



6. Bursting star formation mode

*Section 5.5 explores a bursting mode of star formation. However, the justification for adopting such a mode is unclear. As expected, no significant differences are found, since chemical abundances depend primarily on the time-integrated star formation rate rather than its detailed temporal structure. This result is well known, and the section could be significantly shortened.*

We have cut the bursting star formation model for simplicity.

7. Dwarf galaxy model

 *Dwarf galaxies are characterized by lower star formation rates than the MW disk and by strong galactic winds, which are not observed in the MW. Why the MW model assumes galactic winds? In the MW galactic fountains are more likely than galactic winds. More information about the dwarf model would be welcome.*
*Is the same IMF adopted for both systems? In addition, a plot of [O/Fe] vs. [Fe/H] for the dwarf galaxy should be provided to verify that [O/Fe] declines more steeply than in the MW, as expected.*

We have clarified the description of the dwarf galaxy model and noted that the Milky Way may instead have galactic fountains instead of winds. Since the [O/Fe] vs. [Fe/H] plot for the dwarf galaxy appears as expected for a model with inefficient star formation and high outflows, we chose not to include an additional figure. 