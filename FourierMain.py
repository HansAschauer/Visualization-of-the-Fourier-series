'''
Copyright (C) 2022  https://github.com/aliemen/

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''


### Libraries ###
import numpy as np
import matplotlib.animation as animation # to save the "animation object"

import argparse, os

### My own imports ###
from integral_solver import IS # solve the integrals
from svg_handler import SVG_Handler # handle the svg files as "a function"
from animation import fourier_animation # animate the whole thing


def func_1(t:list):
    ret_arr = np.empty_like(t)
    return ret_arr
    

def get_fourier_coeff(func, T=[0, 1], N=4):
    indizes = np.arange(-N, N+1)
    coeff = np.empty(indizes.shape, dtype=complex)
    
    period = T[1] - T[0]
    for k, ind in enumerate(indizes):
        solver = IS(lambda t: func(t)*np.exp(2j*np.pi*ind/period * t), T)
        coeff[k] = solver.get_approximation(200, n_gauss_param=6)
    
    return indizes, coeff
    

def fourier_eval(ind, coeff, t_eval, period=1):
    if isinstance(t_eval, float) or isinstance(t_eval, int):
        return sum([coeff_t * np.exp(2j*np.pi*ind_t/period * t_eval) for ind_t, coeff_t in zip(ind, coeff)])
        
    ### otherwise, it must be a list... ###
    ret_values = np.zeros(t_eval.shape, dtype=complex)
    
    for i, t_t in enumerate(t_eval):
        ret_values[i] = sum([coeff_t * np.exp(2j*np.pi*ind_t/period * t_t) for ind_t, coeff_t in zip(ind, coeff)])
        #ret_values[i] = ret_values[i-1] + coeff[i] * np.exp(2j*np.pi*ind[i]/period * t_t)

    return ret_values


def get_fourier_vector_line(t, coeff, ind, period=1):
    new_indizes = np.argsort(-np.abs(coeff)) # sort absolute value of coeffs backwards --> print "long" vectors first
    #print(new_indizes)
    coeff_use = coeff[new_indizes]
    ind_use = ind[new_indizes]
    
    ret_line = np.zeros(len(coeff)+1, dtype=complex) # stores all complex values for the line
    ret_line[0] = 0
    for i in range(1, coeff_use.shape[0]+1):
        ret_line[i] = ret_line[i-1] + coeff_use[i-1] * np.exp(2j*np.pi*ind_use[i-1]/period * t) # much much faster...
        #ret_line[i] = fourier_eval(ind_use[:i], coeff_use[:i], t)
    return ret_line

def get_fourier_latex(coeff, ind, coeff_per_line=4): # returns "formatted" latex code to copy the coefficients
    ret_str = "{}&{} " + "{:.4f}".format(coeff[0])
    
    for i, c in enumerate(coeff[1:]):
        if (i+1) % coeff_per_line == 0:
            ret_str += ", " + " \\\\ \n{}&{}" + "{:.4f}".format(c)
        else:
            ret_str += ", " +  "{:.4f}".format(c)
    
    return ret_str.replace('j', 'i')

def get_desmos_string(coeff, ind): # returns 2D vector with sin and cos-funcs to copy into desmos
    def num_f(number, sign=False):
        if sign:
            return "{:+.5f}".format(number).rstrip('0').rstrip('.')
        else:
            return "{:.5f}".format(number).rstrip('0').rstrip('.')
    
    real_string = ""
    imag_string = ""
    
    threshold = 1e-5
    for c, k in zip(coeff, ind):
        #print(num_f(c.real, sign=True))
        if np.abs(c.real) > threshold:
            real_string += f"{num_f(c.real, sign=True)}*cos({2*k}*\\pi*t) "
            
            imag_string += f"{num_f(-c.real, sign=True)}*sin({2*k}*\\pi*t) "
        if np.abs(c.imag) > threshold:
            real_string += f"{num_f(-c.imag, sign=True)}*sin({2*k}*\\pi*t) "
            
            imag_string += f"{num_f(-c.imag, sign=True)}*cos({2*k}*\\pi*t) " # negative sign to "flip" imaginary part (why ever this is necessary)
            
    
    #print(real_string)
    # just makes the string a bit nicer (I know, the following line does not contain nice Code lol)
    return f"({real_string} , {imag_string})".replace(" ", "")#.replace("       ", "").replace("     ", "").replace("    ", "").replace("   ", "").replace("  ", "")

def get_latex_string(coeff, ind): # returns 2D vector with sin and cos-funcs to copy into desmos
    def num_f(number, sign=False):
        if sign:
            return "{:+.5f}".format(number).rstrip('0').rstrip('.')
        else:
            return "{:.5f}".format(number).rstrip('0').rstrip('.')
    
    real_string = ""
    imag_string = ""
    
    threshold = 1e-5
    for c, k in zip(coeff, ind):
        #print(num_f(c.real, sign=True))
        if np.abs(c.real) > threshold:
            real_string += f"{num_f(c.real, sign=True)}\\cos({2*k}\\pi t) "
            
            imag_string += f"{num_f(-c.real, sign=True)}\\sin({2*k}\\pi t) "
        if np.abs(c.imag) > threshold:
            real_string += f"{num_f(-c.imag, sign=True)}\\sin({2*k}\\pi t) "
            
            imag_string += f"{num_f(-c.imag, sign=True)}\\cos({2*k}\\pi t) " # negative sign to "flip" imaginary part (why ever this is necessary)
            
    
    #print(real_string)
    # just makes the string a bit nicer (I know, the following line does not contain nice Code lol)
    #return f"x(t) = {real_string} \ny(t) = {imag_string})"
    return f"""
%\\usepackage{{mathtools}}
%\\usepackage{{amsmath}}

\\begin{{flushleft}}
\\linespread{{2.5}}\\selectfont
\\leftskip=3em
\\hspace*{{-3em}}$\\displaystyle
x(t) = {real_string}
$
\\end{{flushleft}}
\\begin{{flushleft}}
\\linespread{{2.5}}\\selectfont
\\leftskip=3em
\\hspace*{{-3em}}$\\displaystyle
y(t) = {imag_string}
$
\\end{{flushleft}}
"""

# code output function registry
code_output = {
    "latex-coefficients": get_fourier_latex, 
    "desmos-formula": get_desmos_string, 
    "latex-formula": get_latex_string
}

def main():    
    
    # Command line parser
    p = argparse.ArgumentParser()
    p.add_argument("--fourier-coefficients", "-n", type=int, default=30,
                   help="Number of fourier coefficients, will calculate from k=-N up to k=N.")
    p.add_argument("--save-video", "-v", default=False, action="store_true",
                   help="if provided,  save animation as a video (might take some time)")
    p.add_argument("--calculate-only", "-c", default=False, action="store_true",
                   help="Do not show the animation. This is way faster if you just want for example the desmos equation")
    p.add_argument("--simple-plot", "-s", default=False, action="store_true",
                   help="Do not calculate the animation (for 'fast' testing)")
    p.add_argument("--plot-reverse", "-r", action="store_true",default=False, 
                   help="Animates the picture in reverse (for example if you have a text)")
    p.add_argument("--coefficients-output", action="append", choices=code_output.keys(),
                   default=[],
                   help="Output coefficients or formula in provided format to stdandard output. Can be privided multiple times.")
    p.add_argument("--mp4-filename", help="Filname for generated animation (if -v is provided). Defaults to input filename with .mp4 appended.")
    p.add_argument("svg_filename", help="Name of the SVG file")
    args = p.parse_args()
    if args.mp4_filename is None:
        mp4_filename = f"{os.path.splitext(args.svg_filename)}.mp4"
    else:
        mp4_filename = args.mp4_filename
    
    # read svg-file (change path for you own svg-file)
    handler = SVG_Handler(args.svg_filename)
    
    
    save_video = args.save_video
    only_fourier_calc = args.calculate_only
    simple_plot = args.simple_plot
    plot_reverse = args.plot_reverse
    
    
    fourier_N = args.fourier_coefficients # number of fourier coefficients, will calculate from k=-N up to k=N.
                    # In the old version, to many coefficients would have needed much more time.
                    # However, this is not as drastic since 04/15/2022, because the runtime has been improved a lot (explained in GitHub).
    
    T = [0, 1]     # "period" of your image (other intervals will work to, but could break the algorithm if "reverse" is set to true (sorry))
    
    animation_time = 30 # time in seconds that the animation will take
    n_eval = 3000 # number of evaluations on the function (normally "25*animation_time" should be the most efficient)
    t_eval = np.linspace(T[0], T[1], n_eval) 
    
    
    ind, coeff = get_fourier_coeff(lambda t: handler.get_point(t, reverse=plot_reverse), T=T, N=fourier_N) # calculates the fourier coefficients
    print("Calculation of fourier coefficients done.")
    
    # outputs the latex/desmos code (comment out if you don't want it)
    for f in args.coefficients_output:
        print("\n" + code_output[f](coeff, ind) + "\n")

    if not only_fourier_calc:
        ### get the data of the fourier graph ###
        fourier_evaluated = fourier_eval(ind, coeff, t_eval, period=T[1]-T[0])
        figure_data = np.empty((t_eval.shape[0], 2))
        figure_data[:,0] = np.real(fourier_evaluated)
        figure_data[:,1] = -np.imag(fourier_evaluated)
        
        ### get the data for every single "fourier-vector representation" (animation) ###
        if simple_plot:
            fourier_data = None
        else:
            fourier_data = np.empty((t_eval.shape[0], coeff.shape[0]+1, 2))
            for i, time in enumerate(t_eval):
                tmp_vector_line = get_fourier_vector_line(time, coeff, ind)
                fourier_data[i,:,0] = np.real(tmp_vector_line) # x coordinates
                fourier_data[i,:,1] = -np.imag(tmp_vector_line) # y coordinates
                if i % (n_eval // 20) == 0:
                    print(f"{i} of {n_eval} pointers calculated.")
            
        
        print("Calculation of data points from coefficients done.")
        global anim # needs to be global, otherwise the animation will just stop after the algorithm is done
        anim = fourier_animation(figure_data, fourier_data, plot_reference=False or simple_plot, handler=handler, plot_whole_approximation=False or simple_plot,
                                 animation_time=animation_time)
        print("Animation object created.")
        
        ### save a video of the animation ###
        if save_video:
            print("Begin saving the video.")
            Writer = animation.writers['ffmpeg']
            writer = Writer(fps=25, metadata=dict(artist='Me'), bitrate=30000)
            anim.save(mp4_filename, writer=writer)
            print("Done.")
        

if __name__=="__main__":
    main()


