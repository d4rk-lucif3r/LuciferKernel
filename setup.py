from distutils.core import setup
setup(
    name='lucifer-ml',         
    packages=['lucifer'],   
    version='0.0.3c',      
    
    license='MIT',
    
    description="Automated ML by d4rk-lucif3r",
    author='Arsh Anwar',                   
    author_email="lucifer78908@gmail.com",    
    
    url="https://github.com/d4rk-lucif3r/LuciferML",
    
    download_url='https://github.com/d4rk-lucif3r/LuciferML/archive/refs/tags/v_0.0.2.tar.gz',
    
    keywords=['SOME', 'MEANINGFULL', 'KEYWORDS'],
    install_requires=[            
            'numpy',
            'pandas',
            'scipy',
            'seaborn',
            'matplotlib',
            'scikit-learn',
            'imblearn',
            'xgboost',
            'tensorflow',
    ],
    classifiers=[
        
        'Development Status :: 3 - Alpha',
        
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',   
        
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
