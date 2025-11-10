from clash_royale_mega_visualizer_v2 import ClashRoyaleMegaVisualizerV2

viz = ClashRoyaleMegaVisualizerV2()

viz.create_win_rate_usage_bubble().show()
viz.create_rarity_violin_plot().show()
viz.create_archetype_sunburst().show()
viz.create_card_treemap().show()
viz.create_rarity_meta_share().show()

# vis = viz.run_all_visualizations()


# for vis in vis.values():
#     vis.show()
