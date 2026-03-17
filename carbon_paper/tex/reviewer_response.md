> Reviewer comments: 
>
> This paper investigates the stellar production of carbon, with the goal of identifying the dominant carbon producers and the appropriate stellar yields required to reproduce the [C/Fe] abundance ratios observed by APOGEE. The authors test different stellar yield prescriptions for AGB and massive stars using a chemical evolution model of the Milky Way (MW), focusing primarily on the relations [C/Mg] vs. [Mg/H] and [C/Mg] vs. [Mg/Fe].
> Overall, the manuscript is excessively long and, at times, confusing. Several model assumptions are either insufficiently explained or appear questionable. Moreover, the main conclusions are not particularly novel, as similar results have already been reported in previous studies (e.g. Romano et al. 2020). Nevertheless, the paper reflects a substantial amount of work, especially in the systematic testing of different yield sets. For this reason, I do not recommend rejection, but major revisions are required before the paper can be considered for publication.
> My detailed comments are summarized below.

We thank the referee for their detailed review and comments on our manuscript. To shorten the paper and improve clarity, we moved Sections 6 and 7 to the Appendix. Instead, we retain a simplified version of Fig. 9 with a short discussion in Section 5. We have also combined Figs. 1 and 2. We believe that the updates that we have made to the manuscript in response to their input have improved its quality. We detail our specific changes and response to each of the referee's comment below. 



### 1. Choice of abundance diagnostics

> The rationale for adopting the [C/Mg] vs. [Mg/H] and [C/Mg] vs. [Mg/Fe] relations as primary diagnostics is unclear. The origin of a chemical element should be interpreted within the framework of the time-delay model. In this context, the [X/Fe] vs. [Fe/H] relation (where X = C or any other element) is the most informative diagnostic, as it directly reveals whether X is produced on the same timescales as Fe, and therefore by the same stellar sources.
> Approximately 70% of Fe is produced by Type Ia supernovae, with the remaining ~30% originating from core-collapse supernovae (CCSNe). If carbon were mainly produced on the same timescales as Fe, the [C/Fe] vs. [Fe/H] relation would be flat and solar. Conversely, if CCSNe dominate carbon production, one would expect [C/Fe] > 0 at low metallicity ([Fe/H] < −1), as observed for α-elements. Recent observations indeed indicate that [C/Fe] is enhanced at low metallicity, favoring massive stars as the primary carbon producers. This result is not new.
> It is therefore puzzling that the authors do not present or discuss the [C/Fe] ratio, instead focusing on less intuitive diagnostics such as [C/Mg] vs. [Mg/Fe], whose physical interpretation is not explained. It is unclear what additional information can be extracted from these diagrams.
> Furthermore, the manuscript does not mention that Mg yields from massive stars in the literature are highly uncertain and generally underestimated, requiring empirical corrections. This issue directly affects any analysis based on [C/Mg].
> While an increase of [C/Mg] with [Mg/H] is expected if AGB stars contribute to carbon production (as is well established), it is unclear what novel insight is gained by adopting the [C/Mg] ratio. The authors should clarify the motivation and added value of this choice.

We thank the referee for pointing out that we do not properly introduce our chosen abundance ratios. We have added further justification to our chosen yield ratios to the text (in Sections 2 and 5.1) and a new figure (Fig. 6) with a short discussion on utility of the [C/Fe]-[Fe/H] trend (new Section 5.3). 

We believe using [C/Mg] with both [Mg/Fe] and [Fe/H] is necessary to support our argument. By using [C/Mg] with [Mg/Fe], we implicitly study the [C/Fe] abundance trend.  With three elements (C, Mg, and Fe), the [C/Mg]-[Mg/H]-[Mg/Fe] trends also inherently carry more information than the C and Fe abundance trend. Additionally, we disagree that [C/Fe] with [Fe/H] alone is more informative as to carbon's origin than [C/Mg]. In particular, a number of theoretical and observational works suggest that C production by massive stars may be strongly metallicity-dependent, especially in the case of rotating stars (as the referee mentions, e.g., Limongi & Chieffi 2018). As a result, a flat [C/Fe] ratio with metallicity may instead indicate that CCSNe C production increases with metallicity. Using the [C/Fe] versus [Fe/H] to ascertain the origin of C risks confounding metallicity dependence with delayed production, something most previous studies often did not attempt to address. Within a time-delay framework, primary elements produced by delayed sources behave similarly to secondary elements produced in CCSN. This degeneracy is a justification the Romano (2022) review provides for the lack of consensus on the origin of C. Note as well that Romano et al. (2020) test only four yield combinations and acknowledge in their abstract that a more rigorous investigation of carbon is needed. The conflicting results and lack of detailed modelling in the literature regarding the origin of carbon motivates this paper. 

As for the uncertainties in Mg yields, we added a short discussion to Section 4. We simply adopt metallicity-independent yields for Mg and O, as supported by APOGEE abundance trends (e.g., Weinberg et al., 2019). The uncertainties regarding Mg production thus play a minor role in our conclusions. 

### 2. Massive-star yields

> The authors adopt equation (9) to describe the metallicity dependence of carbon yields from massive stars, but its physical meaning and justification are not clearly explained. Why was this specific functional form chosen? Does it accurately reproduce the yields of Limongi & Chieffi (2018)? Additionally, the impact of stellar rotation on the yields, which is known to be significant, should be discussed.
>

We thank the referee for mentioning that Eq. 9 appears to be insufficiently justified. We have clarified this section to better highlight that Eq. 9 was chosen for its simplicity and ability to approximate CCSNe C production including Limongi & Chieffi's (2018) rotating models. 

Our functional form does reasonably reproduce the yields of most CCSN yields in new Fig. 3, including Limongi & Chieffi (2018) and their rotating yield models. We select a linear equation with metallicity also because of its simplicity. The linear form neatly represents a metallicity independent component (primary carbon production) and production proportional to metallicity (secondary carbon production). As noted in the text, more complex models may more accurately represent observed trends and theoretical models, but these models only slightly change our results. 

### 3. Stellar lifetimes

> In Section 3.1, the authors adopt the main-sequence mass–lifetime relation from Larson (1974). This choice is outdated, and more modern prescriptions exist that are consistent with the stellar yields adopted in the paper. A justification for using such an old relation is required.
>

It is true that Larson (1974) is an older model for the mass–lifetime relation. We have added a sentence in the text discussing this choice (in Section 3.1). We have also attached a figure illustrating that adopting the Vincenzo et al. (2016) mass-lifetime relation insignificantly affects the median C abundance trends. 

More recent mass-lifetime relations primarily update the very high or very low mass regimes, leaving the 1–8 solar mass trends nearly unaffected (see appendix A in J. W. Johnson et al. 2023). Our model only depends on the mass–lifetime relation for AGB enrichment, so changing the mass-lifetime relation is not expected to change our results substantially. 



### 4. Chemical evolution model assumptions

> It is unclear whether the chemical evolution model includes gas infall to form the MW disk. The description suggests that only galactic winds may be included. If this is the case, it would be inconsistent with standard MW chemical evolution models. The assumptions regarding infall and outflows should be clearly and explicitly stated.
>

We appreciate the referee's mention of the lack of clarity. Our model does indeed include gas infall, consistent with current GCE models. We have adjusted Section 4 to more explicitly state our model assumptions regarding inflows and outflows. 

### 5. Type Ia supernova delay-time distribution

> The adopted delay-time distribution (DTD) function for Type Ia SNe follows a t⁻¹·¹ dependence, which is reasonable. However, the assumed minimum explosion time of 150 Myr is too long and neglects the existence of prompt Type Ia SNe with delay times shorter than 100 Myr, which are observationally supported, particularly in regions of active star formation (e.g. Mannucci et al. 2006).
> Standard progenitor models for Type Ia SNe involve C–O white dwarfs originating from progenitors with masses up to 8–9 M⊙, implying a minimum delay time of ~30 Myr (Greggio 2005). The most successful chemical evolution models, which reproduce observed abundance patterns and cosmic Type Ia SN rate, include approximately 10% prompt Type Ia SNe (e.g. Palicio et al. 2024). While this issue may not significantly alter the main results, adopting an unrealistically long minimum delay time risks propagating an incorrect assumption. The value of 150 Myr originates from empirical studies of the cosmic Type Ia SN rate, which remains highly uncertain.

We thank the referee for noticing this limitation of the model. We have updated the Type Ia SNe delay-time-distribution, reducing the minimum delay time to 40 Myr and using the time-dependence recommended in Dubay et al. (2024). Dubay et al. (2024) tests different SNIa delay-time-distributions, using a similar VICE chemical evolution model. They conclude that their approximation of Greggio's (2005) WIDE DD model best matches the [alpha/Fe]-[Fe/H] APOGEE trends. This functional form has a DTD which still falls like $t^{-1.1}$ for $t>1$ Gyr, but becomes constant for shorter delay times. While this update affects every model in the paper, the changes to our conclusions are small.



### 6. Bursting star formation mode

> Section 5.5 explores a bursting mode of star formation. However, the justification for adopting such a mode is unclear. As expected, no significant differences are found, since chemical abundances depend primarily on the time-integrated star formation rate rather than its detailed temporal structure. This result is well known, and the section could be significantly shortened.
>

We thank the referee for indicating that Section 5.5 is not well justified. We have moved models exploring variations in the star formation to the appendix. 

We are glad the referee agrees that the SFH should have a minor role in Milky Way trends. However, many astronomers less versed in GCE often interpret all abundance trends in terms of SFH. We retain a comparison of different SFH models in the appendix for readers less familiar with GCE modelling. 

### 7. Dwarf galaxy model

>  Dwarf galaxies are characterized by lower star formation rates than the MW disk and by strong galactic winds, which are not observed in the MW. Why the MW model assumes galactic winds? In the MW galactic fountains are more likely than galactic winds. More information about the dwarf model would be welcome.
> Is the same IMF adopted for both systems? In addition, a plot of [O/Fe] vs. [Fe/H] for the dwarf galaxy should be provided to verify that [O/Fe] declines more steeply than in the MW, as expected.

We appreciate the referee's criticism of the description of the dwarf galaxy model and our assumed Milky Way galactic winds. We have clarified the description of the dwarf galaxy model, and also moved the original Section 7 to the appendix.  We also attach a figure showing that the [Mg/Fe] versus [Fe/H] of the dwarf galaxy  model (with higher outflows and inefficient, rapidly quenching star formation) is as expected compared to the Milky Way model.  We have also added a paragraph discussing the differences between Galactic winds and fountains for chemical evolution in Section 4.



Ultimately, whether gas exits a region through radial gas flows, galactic fountains, or galactic winds is a secondary consideration for GCE models (as added to the discussion in Section 4). All of these processes primarily remove gas from a region and help set the metallicity gradient of the galaxy. Radial gas flows or galactic fountains are effectively equivalent to gas outflows with enriched gas inflows. If the inflows are reasonably diluted by pristine gas, then the additional metallicity content of these inflows has a similar effect to reducing our overall yield scale and outflow strength.  Furthermore, while these is not strong observational evidence for Galactic winds in the Milky Way, the column densities of our outflows would likely be below current detection thresholds (see Veilleux et al., 2020). A more sophisticated model including these (highly uncertain) processes should provide similar results as our simplistic gas outflow model here. 