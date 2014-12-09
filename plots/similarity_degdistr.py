import snap

graph = snap.TUNGraph.Load(snap.TFIn('../similarity.graph'))
snap.PlotInDegDistr(graph, 'similarity_degdistr', 'Degree Distribution: Post Similarity')