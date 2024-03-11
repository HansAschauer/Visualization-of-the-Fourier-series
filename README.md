# Visualization of the Fourier series
Here is some Python code that allows you to read in SVG files and approximate their paths using a Fourier series. The Fourier series can be animated and visualized, the function can be output as a two dimensional vector for Desmos and there is a method to output the coefficients as LaTeX code.

Some example videos of the animations can be found under [example_animations](https://github.com/aliemen/Visualization-of-the-Fourier-series/tree/main/example_animations).

# How to use the program
You will need the packages `numpy`, `matplotlib.pyplot`, `matplotlib.animation`, `svgpathtools` and `scipy.optimize`. 

The most important settings are available via command line arguments:
```bash
usage: FourierMain.py [-h] [--fourier-coefficients FOURIER_COEFFICIENTS] [--save-video] [--calculate-only] [--simple-plot] [--plot-reverse]
                      [--coefficients-output {latex-coefficients,desmos-formula,latex-formula}] [--mp4-filename MP4_FILENAME]
                      svg_filename

positional arguments:
  svg_filename          Name of the SVG file

options:
  -h, --help            show this help message and exit
  --fourier-coefficients FOURIER_COEFFICIENTS, -n FOURIER_COEFFICIENTS
                        Number of fourier coefficients, will calculate from k=-N up to k=N.
  --save-video, -v      if provided, save animation as a video (might take some time)
  --calculate-only, -c  Do not show the animation. This is way faster if you just want for example the desmos equation
  --simple-plot, -s     Do not calculate the animation (for 'fast' testing)
  --plot-reverse, -r    Animates the picture in reverse (for example if you have a text)
  --coefficients-output {latex-coefficients,desmos-formula,latex-formula}
                        Output coefficients or formula in provided format to stdandard output. Can be privided multiple times.
  --mp4-filename MP4_FILENAME
                        Filname for generated animation (if -v is provided). Defaults to input filename with .mp4 appended.
```

####Example
`python FourierMain.py -n 120 images/img4.svg`

This will start a nice animation for `img4.svg`. If you are not interested in the animation, you can provide the `-s` flag, which outputs only the finalized image.

You can even create output in different formats (coefficients or formula in LaTeX, Desmos formula), using the `--coefficients-output` flag.

#### Other settings

Several other settings can be adjusted in the `main` function (file `FourierMain.py`) using the different variables (shortly explained in the code). 

# How to create a usable SVG file
I used [Inkscape](https://inkscape.org/de/) to draw the images. I tested the program with the freehand pen (the result of which can be seen [here](https://www.reddit.com/r/mathmemes/comments/rjvakh/merry_christmas_from_a_complex_fourier_series/), for example) and the Bézier tool. Since the Fourier series at discontinuity points is only (mostly) point convergent and no longer uniformly convergent, one should try to start the new path as close as possible to the end of the old path in the case of several lines. For the same reason, the start and end points of the complete image should be close together.

# What do the internal equations look like?
It is mainly a set of complex polynomials (representations of mostly Bézier curves). These complex polynomials are then parameterized from $t=0$ to $t=1$, depending on the setup, to represent a "partial curve". If we concatenates all partial curves together, we have a large parameterization, which can be normalized by means of the method `_get_parameter_func()` in the file `svg_handler.py` again also to a parameterization for $t\in [0, 1]$. 

## Finding the Fourier coefficients
Once one has the parameterization of the function (which corresponds to the paths of "the image") $\gamma : [0, 1] \rightarrow \mathbb{C}$, one can integrate over the complete function 
$$c_k = \int_0^1 \gamma(t) \cdot e^{2\pi i k \cdot t} \,\text{d}t \quad \text{.}$$ 
Calculating this integral for $N$ coefficients ($k = -N,..., N$), the Fourier series is 
$$f_N(x) = \sum_{-N}^N c_k e^{2\pi i k t}\quad\text{,}$$
which approximates the path of the SVG file. Based on the representation of the curves in the `svgpathtools` library, the image is now described by the two dimensional path 
$$g(t) = \left(\begin{array}{l} \text{Re}(f_N(t)) \\ -\text{Im}(f_N(t)) \end{array}\right)$$ for $t\in [0, 1]$.


## Animation of the "Fourier vector"
Sorting all coefficients by their absolute value and then appending the vectors $g(t)"> for each of the "partial sums $f_N">" with the newly sorted summands, we have a nice looking path the Fourier series takes to approximate a point. If you do this for every single data point of the graph, all plotted one after the other result in the animation. 
