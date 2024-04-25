import pandas as pd
import re
import matplotlib.pyplot as plt

def plot_columns_containing(df, sample, segment = None, exclude=None):
    if segment is not None:
          pattern = rf'{sample}(?![0-9])_{segment}'  
    elif exclude is not None:
        pattern = rf'{sample}(?![0-9])_(?!{exclude})'
    else:
        pattern = rf'{sample}(?![0-9])'
        
        
    cx_columns = [col for col in df.columns if re.search(pattern, col)]
    for col in cx_columns:
        plt.plot(df[col], label=col)
    
    plt.xlabel('Temperatur in °C')
    plt.ylabel('DSC in mW/mg')
    plt.title(f'Plot für Sample "{sample}"')
    plt.legend()
    plt.show()