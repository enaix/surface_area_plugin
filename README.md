# Blender surface area plugin

#### This plugin calculates the surface area of selected faces.

## Installation

Open Blender preferences, go to the Addons tab and manually install `surface_area.py` file.

## Usage

Select `Mesh - Calculate surface area` in Edit mode. The dialog box will appear at the bottom. You may also view it in the recent mesaages history.

## Configuration

`Apply scale transformation to a clone` - Create an object copy instead of applying transformations to the source. Note that it may lead to increased resources usage.

`Use bmesh instead of fast iteration` - Use different API for calculations. Appears to be slower, but doesn't affect calculations.

`Create another context for an object clone` - Create another context for a clone that is going to be destroyed later. Not implemented.

## Notes

If you're using this plugin for calculating materials cost (for example for sewing), note that the actual unwrapped area is bigger. The UV unwrapping area calculation is going to be implemented later.
