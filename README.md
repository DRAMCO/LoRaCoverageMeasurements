# LoRaCoverageMeasurements

## Heatmap Urban
[RSS](http://dramco.be/Measurements/LoRaCoverage/campus/heatmap_RSS.html)
[SNR](http://dramco.be/Measurements/LoRaCoverage/campus/heatmap_SNR.html)

## Heatmap Coastal
[RSS](http://dramco.be/Measurements/LoRaCoverage/seaside/heatmap_RSS.html)
[SNR](http://dramco.be/Measurements/LoRaCoverage/seaside/heatmap_SNR.html)

## Heatmap Forest
[RSS](http://dramco.be/Measurements/LoRaCoverage/forest/heatmap_RSS.html)
[SNR](http://dramco.be/Measurements/LoRaCoverage/forest/heatmap_SNR.html)

## Folder structure
```
├───arduino
│   ├───lib
│   │   └───LoRaLibMod
│   │         Modified LoRa library for our board
│   ├───receiver
│   │         Specific source code (Arduino) for the receiver
│   └───transmitter
│             Specific source code (Arduino) for the trasnmitter
├───data
│     Measurement data
├───processing
│     Python code to process the data and visualize the results
└───result
      Visualization of the results
```
