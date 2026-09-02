terms builder fn: _build_proposal_terms  lines 710-910
  cond=proposal_type in ('armistice_losing', 'armistice')           line 760   terms['type'] = 'armistice_losing'
  cond=proposal_type == 'armistice_stalemate'                       line 764   terms['type'] = 'armistice_losing'
  cond=proposal_type == 'non_aggression'                            line 788   terms['type'] = 'non_aggression'
  cond=proposal_type == 'open_borders'                              line 790   terms['type'] = 'open_borders'
  cond=proposal_type == 'defensive_alliance'                        line 793   terms['type'] = 'defensive_alliance'
  cond=proposal_type == 'alliance'                                  line 796   terms['type'] = 'alliance'
  cond=relation >= 0                                                line 812   terms['type'] = 'non_aggression'
  cond=proposal_type == 'friendly_gift'                             line 814   terms['type'] = 'open_borders'
  cond=proposal_type == 'opportunistic'                             line 824   terms['type'] = 'non_aggression'
  cond=regions and upgrade                                          line 841   terms['type'] = upgrade
  cond=relation >= 0                                                line 874   terms['type'] = 'non_aggression'
  cond=proposal_type == 'sell_neutrality'                           line 876   terms['type'] = 'open_borders'
  cond=proposal_type == 'harsh_peace'                               line 895   terms['type'] = 'peace'
