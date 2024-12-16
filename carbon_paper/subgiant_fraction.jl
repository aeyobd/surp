### A Pluto.jl notebook ###
# v0.20.3

using Markdown
using InteractiveUtils

# ╔═╡ 885a646a-bb42-11ef-256e-551efba18951
begin 
	import Pkg; Pkg.activate()
end

# ╔═╡ f308cdb1-1ebf-4960-a2f4-43ea63e1a277
using OrderedCollections

# ╔═╡ d3a9bbc7-5760-4b5b-a834-e469ff413b88
using Arya

# ╔═╡ 3f661fd0-3328-4eb8-a86b-25f116e7b4af
using CairoMakie

# ╔═╡ 37b81d53-0178-422b-8d0c-5b1f26e7bf72
using PythonCall

# ╔═╡ f68aaa0b-adfc-4d4f-aaa9-4f609cd53a90
using QuadGK

# ╔═╡ fee62bcd-ae70-432e-8baa-442c684e3e03
include("../../dwarfs/utils/read_iso.jl")

# ╔═╡ 39fc692f-d0e9-4263-98d9-aa99978b4f28
filename = "../../dwarfs/MIST/MIST_v1.2_vvcrit0.0_UBVRIplus/MIST_v1.2_feh_p0.00_afe_p0.0_vvcrit0.0_UBVRIplus.iso.cmd"

# ╔═╡ 5957e9a5-6990-4e77-ad42-76e65f051eb1
cmd = ISOCMD(filename)

# ╔═╡ 53968c6e-abee-40bb-a033-63bd4bf4fba3
cmd_lower_mh = ISOCMD("../../dwarfs/MIST/MIST_v1.2_vvcrit0.0_UBVRIplus/MIST_v1.2_feh_m0.25_afe_p0.0_vvcrit0.0_UBVRIplus.iso.cmd")

# ╔═╡ 04aac88d-b3c8-42e2-9724-faf3faab78ca
cmds = OrderedDict(
	"mh-0.25" => ISOCMD("../../dwarfs/MIST/MIST_v1.2_vvcrit0.0_UBVRIplus/MIST_v1.2_feh_m0.25_afe_p0.0_vvcrit0.0_UBVRIplus.iso.cmd"),
	"mh0" => cmd,
	"mh+0.25" => ISOCMD("../../dwarfs/MIST/MIST_v1.2_vvcrit0.0_UBVRIplus/MIST_v1.2_feh_p0.25_afe_p0.0_vvcrit0.0_UBVRIplus.iso.cmd"),
)

# ╔═╡ 04b96d84-f5d4-49c0-8a8e-c0cf456483e4
iso = cmd[9.3]

# ╔═╡ 15ada029-2ad0-44c6-afa1-bc665d3dfea8
function subgiant_filter(iso)
	logg_shift = 0.1
	logg = iso.log_g .+ logg_shift
	teff = 10 .^ iso.log_Teff
	
	mask = @. logg >= 3.5
	mask .&= @. logg <= 0.004*teff - 15.7
	mask .&= @. logg <= 0.0007*teff + 0.36
	mask .&= @. logg <= -0.0015 * teff + 12.05
	mask .&= @. logg >= 0.0012*teff - 2.8

	return mask
end

# ╔═╡ 2ddbcccf-f3e7-4a9c-8607-6b889920ae87
vice = pyimport("vice")

# ╔═╡ 0802417c-f68c-4e25-ad73-6e1488ae52a7
imf = vice.imf.kroupa

# ╔═╡ 1026dd04-ab8b-451e-8816-62c3385ea38e
m_min = 0.08

# ╔═╡ 92e97a48-24b8-4aab-9760-7123a4b4162b
m_max = 100

# ╔═╡ b6978d63-efb8-4062-9390-f128c22f3147
imf(5)

# ╔═╡ fb4f7505-a75e-4f18-a5fe-affe9344892d
imf_norm, _ = quadgk(m -> m*pyconvert(Float64, imf(m)), m_min, m_max)

# ╔═╡ fb2417db-3edb-493d-9846-b62e773f6c63
import StatsBase: midpoints

# ╔═╡ dd2b412b-4a23-48b4-b3e4-4a9e20734784
sum(imf.(midpoints(iso.initial_mass)) .* midpoints(iso.initial_mass ).* diff(iso.initial_mass) ./ imf_norm)

# ╔═╡ b72f5f85-4f96-4ab8-bf79-f75290946ac0
function get_subgiant_number(iso)
	filt = subgiant_filter(iso)[1:end-1]

	masses = iso.initial_mass[1:end-1]
	dm = diff(iso.initial_mass)
	weights = imf.(masses) ./ imf_norm .* dm

	@info "age = $(iso.log10_isochrone_age_yr[1]),     mass = $(sum(weights))"

	return sum(weights[filt])
end

# ╔═╡ 28a3463b-979f-4048-9727-c64bada5a23b
cmd.log_ages

# ╔═╡ 3cca3ee0-f36a-4634-8b53-f5f7047032a4
function get_subgiant_fraction_time(cmd; log_age_min=9)
	age_filt = cmd.log_ages .> log_age_min

	fractions = zeros(sum(age_filt))
	log_ages = cmd.log_ages[age_filt]
	for (i, age) in enumerate(log_ages)
		fractions[i] = pyconvert(Float64, get_subgiant_number(cmd[age]))
	end

	return log_ages, fractions
end
		

# ╔═╡ 9665f536-cc03-46d6-b051-22c7915fd97d
ssp_age, ssp_subgiant_frac = get_subgiant_fraction_time(cmd)

# ╔═╡ 93003bc3-2e4b-4318-8e63-59ba8ed9a150
ssp_age_subgiants = OrderedDict(
	key => get_subgiant_fraction_time(cmd) for (key, cmd) in cmds
)

# ╔═╡ a774fa55-2c35-4c29-82b3-72f23986f24f
ssp_age2, ssp_subgiant_frac2 = get_subgiant_fraction_time(cmd_lower_mh)

# ╔═╡ 845a93f2-85fb-4487-9b66-803cf1348955
let
	fig = Figure(size=(600, 300))
	ax = Axis(fig[1,1],
		xlabel="age / Gyr",
		ylabel = "subgiant fraction",
		limits=(nothing, 14, nothing, nothing)
	)

	for (key, (ssp_age, ssp_subgiant_frac)) in ssp_age_subgiants
		scatterlines!(10 .^ ssp_age ./ 1e9, ssp_subgiant_frac, label=string(key))
	end

	Legend(fig[1,2], ax)
	fig
end

# ╔═╡ 2132937e-75b3-49ec-8d3c-65392b09a735
get_subgiant_number(iso)

# ╔═╡ f476ee68-08c1-4e7b-af9d-a6ec7bee5258
sum(subgiant_filter(iso))

# ╔═╡ 6766e23f-36ce-4461-a973-0e8be5cd186b
coords = [
    (3.5, 4800),
    (3.8, 4875),
    (4.1, 5300),
    (3.8, 5500),
    (3.5, 5250),
    (3.5, 4800)
]

# ╔═╡ 103c066f-ff98-4ee1-bb54-504c7f39f395
let
	fig = Figure()
	ax = Axis(fig[1,1];
		xlabel="Teff", ylabel="logg", yreversed=true,
		xreversed=true,
		limits=(2000, 10_000, 0, 5),
	)

	scatter!(10 .^ iso.log_Teff, iso.log_g .+ 0.1, color=subgiant_filter(iso))
	poly!([coord[[2,1]] for coord in coords], color=:transparent, strokecolor=:black, strokewidth=1)


	fig
end

# ╔═╡ 21f79af5-b1bd-467e-a046-152595e25378
let
	fig = Figure()
	ax = Axis(fig[1,1];
		xlabel="Teff", ylabel="logg", yreversed=true,
		xreversed=true,
		limits=(2000, 10_000, 0, 5),
	)

	age_min = 9
	age_max = log10(13.2e9)

	local p
	for age in cmd.log_ages[age_max .>= cmd.log_ages .> age_min]
		iso = cmd[age]
		p = lines!(10 .^ iso.log_Teff, iso.log_g .+ 0.1, color=age, colorrange=(age_min, age_max))
	end

	
	poly!([coord[[2,1]] for coord in coords], color=:transparent, strokecolor=:black, strokewidth=1)
	
	Colorbar(fig[1,2], colorrange=(age_min, age_max), label="log age / yr")

	fig
end

# ╔═╡ fe45a1a8-404b-434c-89f0-5384cacca3b6
let
	cmd = cmds["mh-0.25"]
	
	fig = Figure()
	ax = Axis(fig[1,1];
		xlabel="Teff", ylabel="logg", yreversed=true,
		xreversed=true,
		limits=(2000, 10_000, 0, 5),
	)

	age_min = 9
	age_max = log10(13.2e9)

	local p
	for age in cmd.log_ages[age_max .>= cmd.log_ages .> age_min]
		iso = cmd[age]
		p = lines!(10 .^ iso.log_Teff, iso.log_g .+ 0.1, color=age, colorrange=(age_min, age_max))
	end

	
	poly!([coord[[2,1]] for coord in coords], color=:transparent, strokecolor=:black, strokewidth=1)
	
	Colorbar(fig[1,2], colorrange=(age_min, age_max), label="log age / Gyr")

	fig
end

# ╔═╡ 2aaab4c0-2c2f-4470-bbb7-abcfcb22feeb
let
	cmd = cmd_lower_mh
	
	fig = Figure()
	ax = Axis(fig[1,1];
		xlabel="Teff", ylabel="logg", yreversed=true,
		xreversed=true,
		limits=(2000, 10_000, 0, 5),
	)

	age_min = 9
	age_max = log10(13.2e9)

	local p
	for age in cmd.log_ages[age_max .>= cmd.log_ages .> age_min]
		iso = cmd[age]
		p = lines!(10 .^ iso.log_Teff, iso.log_g .+ 0.1, color=age, colorrange=(age_min, age_max))
	end

	
	poly!([coord[[2,1]] for coord in coords], color=:transparent, strokecolor=:black, strokewidth=1)
	
	Colorbar(fig[1,2], colorrange=(age_min, age_max), label="log age / Gyr")

	fig
end

# ╔═╡ 42026891-3ad1-43d8-8c95-9e43098e5ea7
let
	fig = Figure()
	cmd = cmds["mh+0.25"]
	ax = Axis(fig[1,1];
		xlabel="Teff", ylabel="logg", yreversed=true,
		xreversed=true,
		limits=(2000, 10_000, 0, 5),
	)

	age_min = 9
	age_max = log10(13.2e9)

	local p
	for age in cmd.log_ages[age_max .>= cmd.log_ages .> age_min]
		iso = cmd[age]
		p = lines!(10 .^ iso.log_Teff, iso.log_g .+ 0.1, color=age, colorrange=(age_min, age_max))
	end

	
	poly!([coord[[2,1]] for coord in coords], color=:transparent, strokecolor=:black, strokewidth=1)
	
	Colorbar(fig[1,2], colorrange=(age_min, age_max), label="log age / Gyr")

	fig
end

# ╔═╡ Cell order:
# ╠═885a646a-bb42-11ef-256e-551efba18951
# ╠═f308cdb1-1ebf-4960-a2f4-43ea63e1a277
# ╠═d3a9bbc7-5760-4b5b-a834-e469ff413b88
# ╠═3f661fd0-3328-4eb8-a86b-25f116e7b4af
# ╠═fee62bcd-ae70-432e-8baa-442c684e3e03
# ╠═39fc692f-d0e9-4263-98d9-aa99978b4f28
# ╠═5957e9a5-6990-4e77-ad42-76e65f051eb1
# ╠═53968c6e-abee-40bb-a033-63bd4bf4fba3
# ╠═04aac88d-b3c8-42e2-9724-faf3faab78ca
# ╠═04b96d84-f5d4-49c0-8a8e-c0cf456483e4
# ╠═15ada029-2ad0-44c6-afa1-bc665d3dfea8
# ╠═37b81d53-0178-422b-8d0c-5b1f26e7bf72
# ╠═2ddbcccf-f3e7-4a9c-8607-6b889920ae87
# ╠═0802417c-f68c-4e25-ad73-6e1488ae52a7
# ╠═1026dd04-ab8b-451e-8816-62c3385ea38e
# ╠═92e97a48-24b8-4aab-9760-7123a4b4162b
# ╠═f68aaa0b-adfc-4d4f-aaa9-4f609cd53a90
# ╠═b6978d63-efb8-4062-9390-f128c22f3147
# ╠═fb4f7505-a75e-4f18-a5fe-affe9344892d
# ╠═fb2417db-3edb-493d-9846-b62e773f6c63
# ╠═dd2b412b-4a23-48b4-b3e4-4a9e20734784
# ╠═b72f5f85-4f96-4ab8-bf79-f75290946ac0
# ╠═28a3463b-979f-4048-9727-c64bada5a23b
# ╠═3cca3ee0-f36a-4634-8b53-f5f7047032a4
# ╠═9665f536-cc03-46d6-b051-22c7915fd97d
# ╠═93003bc3-2e4b-4318-8e63-59ba8ed9a150
# ╠═a774fa55-2c35-4c29-82b3-72f23986f24f
# ╠═845a93f2-85fb-4487-9b66-803cf1348955
# ╠═2132937e-75b3-49ec-8d3c-65392b09a735
# ╠═f476ee68-08c1-4e7b-af9d-a6ec7bee5258
# ╠═6766e23f-36ce-4461-a973-0e8be5cd186b
# ╠═103c066f-ff98-4ee1-bb54-504c7f39f395
# ╠═21f79af5-b1bd-467e-a046-152595e25378
# ╠═fe45a1a8-404b-434c-89f0-5384cacca3b6
# ╠═2aaab4c0-2c2f-4470-bbb7-abcfcb22feeb
# ╠═42026891-3ad1-43d8-8c95-9e43098e5ea7
