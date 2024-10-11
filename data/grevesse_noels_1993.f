! from MESA rvn 3372 chem/public/chem_def.f, same as 3709

      subroutine init_element_atomic_weights
         ! de Laeter et al, Pure and Applied Chemistry 75(6), 683–799, 2003.
         element_atomic_weight(:) = 0

         !periodic table, row 1
         element_atomic_weight(e_h ) = 1.00794
         element_atomic_weight(e_he) = 4.002602

         !periodic table, row 2
         element_atomic_weight(e_li) = 6.941
         element_atomic_weight(e_be) = 9.012
         element_atomic_weight(e_b)  = 10.811
         element_atomic_weight(e_c)  = 12.0107
         element_atomic_weight(e_n)  = 14.0067
         element_atomic_weight(e_o)  = 15.9994
         element_atomic_weight(e_f)  = 18.9984032
         element_atomic_weight(e_ne) = 20.1797

         !periodic table, row 3
         element_atomic_weight(e_na) = 22.989770
         element_atomic_weight(e_mg) = 24.3050
         element_atomic_weight(e_al) = 26.981538
         element_atomic_weight(e_si) = 28.0855
         element_atomic_weight(e_p)  = 30.973761
         element_atomic_weight(e_s)  = 32.065
         element_atomic_weight(e_cl) = 35.453
         element_atomic_weight(e_ar) = 39.948

         !periodic table, row 4
         element_atomic_weight(e_k)  = 39.0983
         element_atomic_weight(e_ca) = 40.078
         element_atomic_weight(e_sc) = 44.955910
         element_atomic_weight(e_ti) = 47.867
         element_atomic_weight(e_v)  = 50.9415
         element_atomic_weight(e_cr) = 51.9961
         element_atomic_weight(e_mn) = 54.938049
         element_atomic_weight(e_fe) = 55.845
         element_atomic_weight(e_co) = 58.933200
         element_atomic_weight(e_ni) = 58.6934
         element_atomic_weight(e_cu) = 63.546
         element_atomic_weight(e_zn) = 65.409
         element_atomic_weight(e_ga) = 69.723
         element_atomic_weight(e_ge) = 72.64
         element_atomic_weight(e_as) = 74.921
         element_atomic_weight(e_se) = 78.96
         element_atomic_weight(e_br) = 79.904
         element_atomic_weight(e_kr) = 83.798

         !periodic table, row 5
         element_atomic_weight(e_rb) = 85.4678
         element_atomic_weight(e_sr) = 87.62
         element_atomic_weight(e_y) =  88.905
         element_atomic_weight(e_zr) = 91.224
         element_atomic_weight(e_nb) = 92.906
         element_atomic_weight(e_mo) = 95.94
         element_atomic_weight(e_tc) = 97.9072
         element_atomic_weight(e_ru) = 101.07
         element_atomic_weight(e_rh) = 102.905
         element_atomic_weight(e_pd) = 106.42
         element_atomic_weight(e_ag) = 107.8682
         element_atomic_weight(e_cd) = 112.411
         element_atomic_weight(e_in) = 114.818
         element_atomic_weight(e_sn) = 118.710
         element_atomic_weight(e_sb) = 121.760
         element_atomic_weight(e_te) = 127.60
         element_atomic_weight(e_i ) = 126.904
         element_atomic_weight(e_xe) = 131.293

         !periodic table, row 6
         element_atomic_weight(e_cs) = 132.905
         element_atomic_weight(e_ba) = 137.327
         element_atomic_weight(e_la) = 138.9055
         element_atomic_weight(e_ce) = 140.115
         element_atomic_weight(e_pr) = 140.90765
         element_atomic_weight(e_nd) = 144.24
         element_atomic_weight(e_pm) = 144.9127
         element_atomic_weight(e_sm) = 150.36
         element_atomic_weight(e_eu) = 151.965
         element_atomic_weight(e_gd) = 157.25
         element_atomic_weight(e_tb) = 158.92534
         element_atomic_weight(e_dy) = 162.50
         element_atomic_weight(e_ho) = 164.93032
         element_atomic_weight(e_er) = 167.26
         element_atomic_weight(e_tm) = 168.93421
         element_atomic_weight(e_yb) = 173.04
         element_atomic_weight(e_lu) = 174.967
         element_atomic_weight(e_hf) = 178.49
         element_atomic_weight(e_ta) = 180.9479
         element_atomic_weight(e_w ) = 183.84
         element_atomic_weight(e_re) = 186.207
         element_atomic_weight(e_os) = 190.23
         element_atomic_weight(e_ir) = 192.22
         element_atomic_weight(e_pt) = 195.08
         element_atomic_weight(e_au) = 196.96654
         element_atomic_weight(e_hg) = 200.59
         element_atomic_weight(e_tl) = 204.3833
         element_atomic_weight(e_pb) = 207.2
         element_atomic_weight(e_bi) = 208.98037
         element_atomic_weight(e_po) = 208.9824
         element_atomic_weight(e_at) = 209.9871

      end subroutine init_element_atomic_weights

      subroutine init_GN93_data ! fraction by mass of total Z
         ! Grevesse and Noels 1993
         integer :: i
         double precision :: Y_H, sum_X, Y_i  
         GS98_element_zfrac(:) = 0
         include 'formats.dek'         


         GN93_element_zfrac(:) = 0
         
        !GN93_element_zfrac(e_H)=12.00
        !GN93_element_zfrac(e_He)=10.99
         GN93_element_zfrac(e_Li)=3.31 !meteor
         GN93_element_zfrac(e_Be)=1.42 !meteor
         GN93_element_zfrac(e_B )=2.79  !meteor
         GN93_element_zfrac(e_C )=8.55
         GN93_element_zfrac(e_N )=7.97
         GN93_element_zfrac(e_O )=8.87
         GN93_element_zfrac(e_F )=4.48
         GN93_element_zfrac(e_Ne)=8.08
         GN93_element_zfrac(e_Na)=6.33
         GN93_element_zfrac(e_Mg)=7.58
         GN93_element_zfrac(e_Al)=6.47
         GN93_element_zfrac(e_Si)=7.55
         GN93_element_zfrac(e_P )=5.45
         GN93_element_zfrac(e_S )=7.20
         GN93_element_zfrac(e_Cl)=5.28
         GN93_element_zfrac(e_Ar)=6.52
         GN93_element_zfrac(e_K )=5.12
         GN93_element_zfrac(e_Ca)=6.36
         GN93_element_zfrac(e_Sc)=3.17
         GN93_element_zfrac(e_Ti)=5.02
         GN93_element_zfrac(e_V )=4.00
         GN93_element_zfrac(e_Cr)=5.67
         GN93_element_zfrac(e_Mn)=5.39
         GN93_element_zfrac(e_Fe)=7.50
         GN93_element_zfrac(e_Co)=4.92
         GN93_element_zfrac(e_Ni)=6.25
         GN93_element_zfrac(e_Cu)=4.21
         GN93_element_zfrac(e_Zn)=4.60
         GN93_element_zfrac(e_Ga)=3.13
         GN93_element_zfrac(e_Ge)=3.41
         GN93_element_zfrac(e_As)=2.37
         GN93_element_zfrac(e_Se)=3.38
         GN93_element_zfrac(e_Br)=2.63
         GN93_element_zfrac(e_Kr)=3.23
         GN93_element_zfrac(e_Rb)=2.41
         GN93_element_zfrac(e_Sr)=2.97
         GN93_element_zfrac(e_Y )=2.24
         GN93_element_zfrac(e_Zr)=2.60
         GN93_element_zfrac(e_Nb)=1.42
         GN93_element_zfrac(e_Mo)=1.92
         GN93_element_zfrac(e_Ru)=1.84
         GN93_element_zfrac(e_Rh)=1.12
         GN93_element_zfrac(e_Pd)=1.69
         GN93_element_zfrac(e_Ag)=1.24
         GN93_element_zfrac(e_Cd)=1.77
         GN93_element_zfrac(e_In)=0.82
         GN93_element_zfrac(e_Sn)=2.14
         GN93_element_zfrac(e_Sb)=1.03
         GN93_element_zfrac(e_Te)=2.24
         GN93_element_zfrac(e_I )=1.51
         GN93_element_zfrac(e_Xe)=2.23
         GN93_element_zfrac(e_Cs)=1.13
         GN93_element_zfrac(e_Ba)=2.13
         GN93_element_zfrac(e_La)=1.17
         GN93_element_zfrac(e_Ce)=1.58
         GN93_element_zfrac(e_Pr)=0.71
         GN93_element_zfrac(e_Nd)=1.50
         GN93_element_zfrac(e_Sm)=1.01
         GN93_element_zfrac(e_Eu)=0.51
         GN93_element_zfrac(e_Gd)=1.12
         GN93_element_zfrac(e_Tb)=0.35
         GN93_element_zfrac(e_Dy)=1.14
         GN93_element_zfrac(e_Ho)=0.51
         GN93_element_zfrac(e_Er)=0.93
         GN93_element_zfrac(e_Tm)=0.15
         GN93_element_zfrac(e_Yb)=1.08
         GN93_element_zfrac(e_Lu)=0.13
         GN93_element_zfrac(e_Hf)=0.88
         GN93_element_zfrac(e_Ta)=-0.13
         GN93_element_zfrac(e_W )=0.69
         GN93_element_zfrac(e_Re)=0.28
         GN93_element_zfrac(e_Os)=1.45
         GN93_element_zfrac(e_Ir)=1.37
         GN93_element_zfrac(e_Pt)=1.69
         GN93_element_zfrac(e_Au)=0.87
         GN93_element_zfrac(e_Hg)=1.17
         GN93_element_zfrac(e_Tl)=0.83
         GN93_element_zfrac(e_Pb)=2.06
         GN93_element_zfrac(e_Bi)=0.71
         !GN93_element_zfrac(e_Th)=0.09 ! Th and U are not included
         !GN93_element_zfrac(e_U)=-0.50 ! in chem at present



         ! convert to mass fractions
         Y_H = 1.0 - (GN93_zsol + GN93_ysol)/element_atomic_weight(e_h)
         do i = e_li, e_bi
            Y_i = Y_H*10**(GN93_element_zfrac(i) - 12d0)
            GN93_element_zfrac(i) = Y_i*element_atomic_weight(i)
         end do

         if (report_solar .or. abs(sum(GN93_element_zfrac)-GN93_zsol) > 1d-3 ) then
            write(*,1)'sum(GN93_element_zfrac)', sum(GN93_element_zfrac)
            write(*,1)'GN93_zsol', GN93_zsol
            write(*,1)'sum - GN93_zsol', sum(GN93_element_zfrac)-GN93_zsol
            write(*,*)
            write(*,1) 'X_C/Z', GN93_element_zfrac(e_c)/GN93_zsol
            write(*,1) 'X_N/Z', GN93_element_zfrac(e_n)/GN93_zsol
            write(*,1) 'X_O/Z', GN93_element_zfrac(e_o)/GN93_zsol
            write(*,1) 'X_Ne/Z', GN93_element_zfrac(e_ne)/GN93_zsol
            write(*,*)
            !stop 1
         end if
         
         GN93_element_zfrac = GN93_element_zfrac / sum(GN93_element_zfrac(:))

      end subroutine init_GN93_data

         

