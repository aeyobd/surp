Nr = len(plot_labels)
fig, axs = plt.subplots(Nr, 1, figsize=(3, 2), sharex="col", gridspec_kw={"hspace": 0})

for i, (key, label) in enumerate(plot_labels.items()):
    if key == "hline":
        ax = axs[i]
        plt.sca(axs[i])
        ax.spines[['bottom', 'top']].set_visible(False)
        plt.axhline(0.5, color=label, linestyle=":")
        ax.xaxis.set_visible(False)
        ax.set_yticks([])
        ax.set_yticks([], minor=True)
        
        continue

    if i < 5:
        color = arya.COLORS[i]
        ls = "-"
    else:
        ls = "--"
        color = arya.COLORS[0]

    result = results[key]
    ax = axs[i]
    plt.sca(axs[i])
    plt.hist(result.samples.f_agb_a, color=color, ls=ls)
    plt.ylabel(label, rotation=0, ha="right", va="center")

    if key in yagb_props.keys():
        y_a = yagb_props[key]["y_a"]
    elif key == "fruity_m0.7":
        y_a = yagb_props["fruity_mf0.7"]["y_a"]
    else:
        print(f"warning, {key} not found")
        y_a = yagb_props["fruity"]["y_a"]

    f0 = y_a / 2.79e-3
    print("f = ", f0, " key, ", key)
    plt.scatter(f0, 0, c="black", edgecolors="black", lw=1, marker="x")
    plt.scatter(f0, 0, c=color, edgecolors="black", lw=0.5, marker="x")

    if Nr - 1 > i > 0:
        ax.spines[['bottom', 'top']].set_visible(False)
        ax.xaxis.set_visible(False)
    elif i == 0:
        ax.spines[['bottom']].set_visible(False)
        ax.tick_params(axis='x',  bottom=False, which="both")
    elif i == Nr - 1:
        ax.spines[['top']].set_visible(False)
        ax.tick_params(axis='x',  top=False, which="both")


    ax.set_yticks([])
    ax.set_yticks([], minor=True)
    plt.ylim(-1000)



plt.sca(axs[-1])
plt.xlabel(r"$f_{\rm AGB}$")
plt.xlim(0, 0.6)

plt.tight_layout()
plt.savefig("figures/mcmc_fagb.pdf")
plt.savefig("figures/mcmc_fagb.png")
