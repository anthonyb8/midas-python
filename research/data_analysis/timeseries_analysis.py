import numpy as np
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.tsa.vector_ar.vecm import coint_johansen, VECM, select_coint_rank
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.stats.stattools import durbin_watson
from statsmodels.tsa.stattools import grangercausalitytests
from statsmodels.stats.diagnostic import het_breuschpagan, het_white
from scipy.stats import shapiro
import scipy.stats as stats
from arch.unitroot import PhillipsPerron
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.vector_ar.var_model import VAR
import seaborn as sns
from scipy.stats import norm


pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 1000) # Adjust the width of the display in characters
pd.set_option('display.max_rows', None)


class TimeseriesTests:
    """
    Easy use and display of the results from statsmodels tests, for timerseries analysis.
    """
    # -- Stationarity -- 
    @staticmethod
    def adf_test(series: pd.Series, trend='c', confidence_interval='5%'):
        """Perform Augmented Dickey-Fuller test and return results with stationarity indication."""

        result = adfuller(x=series, regression=trend)
        adf_statistic = result[0]
        p_value = result[1]
        critical_values = result[4]

        # Prepare the results in a clean format
        output = {
            'ADF Statistic': adf_statistic,
            'p-value': p_value,
            'Critical Values': critical_values,
            'Stationarity': ''
        }

        # Determine stationarity based on the specified confidence interval and p-value
        stationarity = adf_statistic < critical_values[confidence_interval] and p_value < 0.05

        output['Stationarity'] = 'Stationary' if stationarity else 'Non-Stationary'

        return output

    @staticmethod
    def display_adf_results(adf_results:dict, print_output: bool = True, to_html: bool = False):
        # Convert ADF results to DataFrame
        adf_data = []
        for ticker, values in adf_results.items():
            row = {'Ticker': ticker, 'ADF Statistic': values['ADF Statistic'], 'p-value': round(values['p-value'],6)}
            row.update({f'Critical Value ({key})': val for key, val in values['Critical Values'].items()})
            row.update({'Stationarity': values['Stationarity']})
            adf_data.append(row)

        title = "ADF Test Results"
        adf_df = pd.DataFrame(adf_data)
        footer = "** IF p-value < 0.05 and/or statistic < statistic @ confidence interval, then REJECT the Null that the time series posses a unit root (non-stationary).\n"

        if to_html:
            # Convert DataFrame to HTML table and add explanation
            html_table = adf_df.to_html(index=False, border=1)
            html_explanation = f"<p>{footer}</p>"
            html_output = f"<h2>{title}</h2>\n{html_table}\n{html_explanation}"
            return html_output
        elif print_output:
            print(f"""\n{title}:
                    {'=' * len(title)}
                    {adf_df}
                    {footer}
                """)
        else:
            return (
                f"\n{title}\n"
                f"{'=' * len(title)}\n"
                f"{adf_df.to_string(index=False)}\n"
                f"{footer}"
            )
        
    @staticmethod
    def kpss_test(series: pd.Series,trend='c', confidence_interval='5%'):

        """Perform KPSS test and return results with stationarity indication."""
        kpss_statistic, p_value, n_lags, critical_values = kpss(x=series, regression=trend)

        # Prepare the results in a structured format
        output = {
            'KPSS Statistic': kpss_statistic,
            'p-value': p_value,
            'Critical Values': critical_values,
            'Stationarity': ''
        }

        # Determine stationarity based on the 1% confidence interval
        stationarity = kpss_statistic < critical_values[confidence_interval]

        output['Stationarity'] = 'Stationary' if stationarity else 'Non-Stationary'

        return output
    
    @staticmethod
    def display_kpss_results(kpss_results:dict, print_output: bool=True, to_html: bool = False):
        # Convert KPSS results to DataFrame
        kpss_data = []
        for ticker, values in kpss_results.items():
            row = {'Ticker': ticker, 'KPSS Statistic': values['KPSS Statistic'], 'p-value': round(values['p-value'],6)}
            row.update({f'Critical Value ({key})': val for key, val in values['Critical Values'].items()})
            row.update({'Stationarity': values['Stationarity']})
            kpss_data.append(row)

        title = "KPSS Test Results"
        kpss_df = pd.DataFrame(kpss_data)
        footer = "** IF KPSS statistic > statistic @ confidence interval, then reject the NUll that time-series is stationary.\n"

        if to_html:
            # Convert DataFrame to HTML table and add explanation
            html_table = kpss_df.to_html(index=False, border=1)
            html_explanation = f"<p>{footer}</p>"
            html_output = f"<h2>{title}</h2>\n{html_table}\n{html_explanation}"
            return html_output
        elif print_output:
            print(f"""\n{title}:
                    {'=' * len(title)}
                    {kpss_df}
                    {footer}
                """)
        else:
            return (
                f"\n{title}\n"
                f"{'=' * len(title)}\n"
                f"{kpss_df.to_string(index=False)}\n"
                f"{footer}"
            )

    @staticmethod
    def phillips_perron_test(series: pd.Series, trend='c', confidence_interval='5%'):
        """
        Perform Phillips-Perron test and return results with stationarity indication.

        Args:
        series (pd.Series): The time series to be tested.
        trend (str): Type of regression applied in the test ('c' for constant, 'ct' for constant and trend, etc.).
        confidence_interval (str): Confidence interval for the critical values ('1%', '5%', '10%', etc.).

        Returns:
        dict: A dictionary with test statistic, p-value, critical values, and stationarity indication.
        """
        pp_test = PhillipsPerron(series, trend=trend)
        pp_statistic = pp_test.stat
        p_value = pp_test.pvalue
        critical_values = pp_test.critical_values

        # Prepare the results in a clean format
        output = {
            'PP Statistic': pp_statistic,
            'p-value': p_value,
            'Critical Values': critical_values,
            'Stationarity': ''
        }

        # Determine stationarity based on the specified confidence interval and p-value
        stationarity = pp_statistic < critical_values[confidence_interval] and p_value < 0.05

        output['Stationarity'] = 'Stationary' if stationarity else 'Non-Stationary'

        return output
    
        return output

    @staticmethod
    def display_pp_results(pp_results: dict, print_output: bool=True, to_html: bool = False):
        # Convert PP results to DataFrame
        pp_data = []
        for ticker, values in pp_results.items():
            row = {
                'Ticker': ticker, 
                'PP Statistic': values['PP Statistic'], 
                'p-value': round(values['p-value'], 6)
            }
            row.update({f'Critical Value ({key}%)': val for key, val in values['Critical Values'].items()})
            row.update({'Stationarity': values['Stationarity']})
            pp_data.append(row)

        title = "Phillips Perron Results"
        pp_df = pd.DataFrame(pp_data)
        footer = "** IF p-value < 0.05, then REJECT the Null Hypothesis of a unit root (non-stationary time series).\n"

        if to_html:
            # Convert DataFrame to HTML table and add explanation
            html_table = pp_df.to_html(index=False, border=1)
            html_explanation = f"<p>{footer}</p>"
            html_output = f"<h2>{title}</h2>\n{html_table}\n{html_explanation}"
            return html_output
        elif print_output:
            print(f"""\n{title}:
                    {'=' * len(title)}
                    {pp_df}
                    {footer}
                """)
        else:
            return (
                f"\n{title}\n"
                f"{'=' * len(title)}\n"
                f"{pp_df.to_string(index=False)}\n"
                f"{footer}"
            )
        
    @staticmethod
    def seasonal_adf_test(series, maxlag=None, regression='c', seasonal_periods=12, confidence_interval='5%'):
        """
        Perform Seasonal Augmented Dickey-Fuller test.
        :param series: Time series data.
        :param maxlag: Maximum number of lags to include in the test.
        :param regression: Type of regression ('c', 'ct', 'ctt', 'nc').
        :param seasonal_periods: Number of periods in a season.
        :return: Dictionary with test results.
        """
        dftest = sm.tsa.seasonal_decompose(series, model='additive', period=seasonal_periods)
        detrended = series - dftest.trend
        result = sm.tsa.adfuller(detrended.dropna(), maxlag=maxlag, regression=regression, autolag='AIC')

        adf_statistic = result[0]
        p_value = result[1]
        critical_values = result[4]
        
        # Prepare the results in a clean format
        output = {
            'ADF Statistic': adf_statistic,
            'p-value': p_value,
            'Critical Values': critical_values,
            'Stationarity': ''
        }
        
        # Determine stationarity based on the specified confidence interval and p-value
        stationarity = adf_statistic < critical_values[confidence_interval] and p_value < 0.05

        output['Stationarity'] = 'Stationary' if stationarity else 'Non-Stationary'

        return output
    

    # -- Cointegration --
    @staticmethod
    def johansen_test(data:pd.DataFrame, det_order=-1, k_ar_diff=1):
        """Perform Johansen cointegration test and return structured results with analysis."""
        result = coint_johansen(data, det_order, k_ar_diff)

        # Prepare the results in a structured format
        output = {
            'Eigenvalues': result.eig,
            'Critical Values for Trace Statistic': result.cvt[:, 0],
            'Critical Values for Max Eigenvalue Statistic': result.cvt[:, 1],
            'Trace Statistics': result.lr1,
            'Max Eigenvalue Statistics': result.lr2,
            'Cointegrating Vector': list(result.evec)
        }

        # Analysis of Trace and Max Eigenvalue Statistics
        num_cointegrations = 0
        trace_analysis = []
        max_eig_analysis = []

        for idx, (trace_stat, max_eig_stat) in enumerate(zip(output['Trace Statistics'], output['Max Eigenvalue Statistics'])):
            trace_crit_value = output['Critical Values for Trace Statistic'][idx]
            max_eig_crit_value = output['Critical Values for Max Eigenvalue Statistic'][idx]

            trace_decision = trace_stat > trace_crit_value
            max_eig_decision = max_eig_stat > max_eig_crit_value

            trace_analysis.append(f'Hypothesis {idx}: {"Reject" if trace_decision else "Fail to Reject"} the null hypothesis of no cointegration at this level.')
            max_eig_analysis.append(f'Hypothesis {idx}: {"Reject" if max_eig_decision else "Fail to Reject"} the null hypothesis of no cointegration at this level.')

            if trace_decision and max_eig_decision:
                num_cointegrations += 1


        return output, num_cointegrations
    
    @staticmethod
    def display_johansen_results(johansen_results:dict, num_cointegrations:int, print_output: bool=True, to_html: bool = False):
        # Creating DataFrame from the results
        johansen_df = pd.DataFrame({
            'Hypothesis': [f'H{i}' for i in range(len(johansen_results['Eigenvalues']))],
            'Eigenvalue': johansen_results['Eigenvalues'],
            'Trace Statistic': johansen_results['Trace Statistics'],
            'Critical Value (Trace)': johansen_results['Critical Values for Trace Statistic'],
            'Max Eigenvalue Statistic': johansen_results['Max Eigenvalue Statistics'],
            'Critical Value (Max Eigenvalue)': johansen_results['Critical Values for Max Eigenvalue Statistic'],
        })

        # Add decision columns based on comparisons
        johansen_df['Decision (Trace)'] = johansen_df.apply(
            lambda row: 'Reject' if row['Trace Statistic'] > row['Critical Value (Trace)'] else 'Fail to Reject',
            axis=1
        )
        johansen_df['Decision (Max Eigenvalue)'] = johansen_df.apply(
            lambda row: 'Reject' if row['Max Eigenvalue Statistic'] > row['Critical Value (Max Eigenvalue)'] else 'Fail to Reject',
            axis=1
        )
        
        title = "Johansen Cointegration Test Results"
        header = f"\nNumber of cointerated realtionships : {num_cointegrations}\n"
        footer = f"** IF Trace Statistic > Critical Value AND Max Eigenvalue > Critical Value then Reject Null of at most r cointegrating relationships.(r=0 in first test)\n"

        if to_html:
            # Convert DataFrame to HTML table and add explanation
            html_table = johansen_df.to_html(index=False, border=1)
            html_header = f"<h2>Johansen Cointegration Test Results</h2><p>{header}</p>"
            html_footer = f"<p>{footer}</p>"
            html_output = f"{html_header}\n{html_table}\n{html_footer}"
            return html_output
        elif print_output:
            print(f"""\n{title}:
                    {'=' * len(title)}
                    {header}
                    {johansen_df}
                    {footer}
                """)
        else:
            return (
                f"\n{title}\n"
                f"{'=' * len(title)}\n"
                f"{header}\n"
                f"{johansen_df.to_string(index=False)}\n"
                f"{footer}"
            )
        
    @staticmethod
    def select_lag_length(data:pd.DataFrame, maxlags=10):
        """
        Selects the optimal lag length for a time series data set based on information criteria.

        Args:
        data (DataFrame): A pandas DataFrame containing the time series data.
        maxlags (int): The maximum number of lags to test.

        Returns:
        int: The optimal number of lags.
        """
        # Ensure data is a pandas DataFrame
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Data must be a pandas DataFrame.")

        # Initialize variables to store the best lag and its corresponding criterion value
        best_lag = 0
        best_criterion = float('inf')

        # Iterate over possible lag values
        for lag in range(1, maxlags + 1):
            # Fit a Vector AutoRegression (VAR) model as VECM is not directly supported for lag selection
            model = VAR(data)
            result = model.fit(lag)

            # You can choose different criteria here, such as AIC, BIC, FPE, or HQIC
            # Modify this line to use a different criterion if needed
            criterion_value = result.aic

            # Update the best lag if this is the best criterion value so far
            if criterion_value < best_criterion:
                best_criterion = criterion_value
                best_lag = lag

        return best_lag

    @staticmethod
    def select_coint_rank(data, k_ar_diff, method='trace', signif=0.05, det_order=-1):
        """
        Selects the cointegration rank for a dataset.

        Args:
        data (DataFrame): A pandas DataFrame containing the time series data.
        k_ar_diff (int): The number of lags to be used.
        method (str): The test method ('trace' or 'maxeig').
        signif (float): Significance level for the test.
        det_order (int): The order of the deterministic trend (constant, linear trend, etc.).

        Returns:
        CointRankResults: The results of the cointegration rank selection.
        """
        coint_rank_results = select_coint_rank(data, det_order=det_order, k_ar_diff=k_ar_diff, method=method, signif=signif)
        return coint_rank_results


    # -- Autocorrelation -- 
    @staticmethod
    def durbin_watson(residuals:pd.DataFrame):
        """
        Perform the Durbin-Watson test on the residuals of a model.

        Args:
        residuals (DataFrame): A pandas DataFrame or numpy array of residuals from a regression model.

        Returns:
        dict: A dictionary with keys as column names and values as Durbin-Watson statistics.
        """
        dw_stats = {}
        for col in residuals.columns:
            dw_stat = durbin_watson(residuals[col])
            # Autocorrelation interpretation (rule of thumb): 
            # dw_stat < 1.5 (positive autocorrelation), dw_stat > 2.5 (negative autocorrelation), otherwise no autocorrelation
            autocorrelation = 'Absent'
            if dw_stat < 1.5:
                autocorrelation = 'Positive'
            elif dw_stat > 2.5:
                autocorrelation = 'Negative'

            dw_stats[col] = {
                'Durbin-Watson Statistic': dw_stat,
                'Autocorrelation': autocorrelation
            }
        return dw_stats
    
    @staticmethod 
    def display_durbin_watson_results(dw_results:dict, print_output: bool=True, to_html: bool = False):
        # Convert Durbin-Watson results to DataFrame
        dw_data = []
        for ticker, values in dw_results.items():
            row = {
                'Ticker': ticker, 
                'Durbin-Watson Statistic': values['Durbin-Watson Statistic'], 
                'Autocorrelation': values['Autocorrelation']
            }
            dw_data.append(row)

        dw_df = pd.DataFrame(dw_data)
        footnote = "** If the Durbin-Watson statistic is significantly different from 2 (either much less than 2 or much greater than 2), it suggests the presence of autocorrelation in the residuals.\n"

        if to_html:
            # Convert DataFrame to HTML table and add explanation
            html_table = dw_df.to_html(index=False, border=1)
            html_explanation = f"<p>{footnote}</p>"
            html_output = f"<h2>Durbin Watson Results</h2>\n{html_table}\n{html_explanation}"
            return html_output
        elif print_output:
            print(f"Durbin Watson Results:\n{dw_df}\n{footnote}")
        else:
            return f"Durbin Watson Results:\n{dw_df.to_string(index=False)}\n{footnote}"
    
    @staticmethod
    def ljung_box(residuals:pd.DataFrame, lags:int, significance_level:float=0.05):
        """
        Perform the Ljung-Box test on the residuals of a model.

        Args:
        residuals (DataFrame): A pandas DataFrame or numpy array of residuals from a regression model.
        lags (int or array): The number of lags to include in the test, or the specific lags to test.
        significance_level (float): The significance level for statistical testing.

        Returns:
        dict: A dictionary with keys as column names and values as dictionaries containing test statistics, p-values, and autocorrelation indication.
        """
        lb_results = {}
        for col in residuals.columns:
            lb_test = acorr_ljungbox(residuals[col], lags=lags, return_df=True)
            is_autocorrelated = any(lb_test['lb_pvalue'].values < significance_level)
            lb_results[col] = {
                'test_statistic': lb_test['lb_stat'].values,
                'p_value': lb_test['lb_pvalue'].values,
                'significance': lb_test['lb_pvalue'].values < significance_level,
                'Autocorrelation': 'Present' if is_autocorrelated else 'Absent'
            }
        return lb_results

    @staticmethod
    def display_ljung_box_results(ljung_box_results:dict, print_output: bool=True, to_html: bool = False):
        # Convert Ljung-Box results to DataFrame
        ljung_box_data = []
        for ticker, values in ljung_box_results.items():
            row = {'Ticker': ticker, 'Test Statistic': values['test_statistic'][0], 'p-value': round(values['p_value'][0], 6)}
            row.update({'Autocorrelation': 'Absent' if values['significance'][0] == False else 'Present'})
            ljung_box_data.append(row)

        ljung_box_df = pd.DataFrame(ljung_box_data)
        footnote = "** IF p-value < 0.05, then REJECT the Null Hypothesis of no autocorrelation (i.e., autocorrelation is present).\n"
    
        if to_html:
            # Convert DataFrame to HTML table and add explanation
            html_table = ljung_box_df.to_html(index=False, border=1)
            html_explanation = f"<p>{footnote}</p>"
            html_output = f"<h2>Ljung-Box Results</h2>\n{html_table}\n{html_explanation}"
            return html_output
        elif print_output:
            print(f"Ljung-Box Results:\n{ljung_box_df}\n{footnote}")
        else:
            return f"Ljung-Box Results:\n{ljung_box_df.to_string(index=False)}\n{footnote}"
    
    # -- Normality -- 
    @staticmethod
    def shapiro_wilk(data:pd.Series, significance_level:float=0.05):
        """
        Perform the Shapiro-Wilk Test for normality.

        Args:
        data (Series or array-like): The data on which to perform the test.
        significance_level (float): The significance level to determine normality.

        Returns:
        dict: Test statistic, p-value, and normality indication.
        """
        stat, p_value = shapiro(data)

        # Determine normality based on the p-value
        normality = 'Normal' if p_value >= significance_level else 'Not Normal'

        return {
            'Statistic': stat,
            'p-value': p_value,
            'Normality': normality
        }

    @staticmethod
    def display_shapiro_wilk_results(sw_results:dict, print_output:bool=True, to_html: bool = False):
        # Convert Shapiro-Wilk results to DataFrame
        sw_data = []
        for ticker, values in sw_results.items():
            row = {
                'Ticker': ticker, 
                'Shapiro-Wilk Statistic': values['Statistic'], 
                'p-value': values['p-value'], 
                'Normality': values['Normality']
            }
            sw_data.append(row)

        sw_df = pd.DataFrame(sw_data)
        footnote = "** If p-value < 0.05, then REJECT the Null Hypothesis of normality (i.e., data is not normally distributed).\n"

        if to_html:
            # Convert DataFrame to HTML table and add explanation
            html_table = sw_df.to_html(index=False, border=1)
            html_explanation = f"<p>{footnote}</p>"
            html_output = f"<h2>Shapiro Wilk Results</h2>\n{html_table}\n{html_explanation}"
            return html_output
        elif print_output:
            print(f"Shapiro Wilk Results:\n{sw_df}\n{footnote}")
        else:
            return f"Shapiro Wilk Results:\n{sw_df.to_string(index=False)}\n{footnote}"
    
    @staticmethod
    def histogram_ndc(data:pd.Series, bins='auto', title='Histogram with Normal Distribution Curve'):
        """
        Create a histogram for the given data and overlay a normal distribution fit.

        Args:
        data (array-like): The dataset for which the histogram is to be created.
        bins (int or sequence or str): Specification of bin sizes. Default is 'auto'.
        title (str): Title of the plot.

        Returns:
        matplotlib figure: A histogram with a normal distribution fit.
        """
        # Convert data to a numpy array if it's not already
        data = np.asarray(data)

        # Generate histogram
        plt.figure(figsize=(10, 6))
        sns.histplot(data, bins=bins, kde=False, color='blue', stat="density")

        # Fit and overlay a normal distribution
        mean, std = norm.fit(data)
        xmin, xmax = plt.xlim()
        x = np.linspace(xmin, xmax, 100)
        p = norm.pdf(x, mean, std)
        plt.plot(x, p, 'k', linewidth=2)

        title += f'\n Fit Results: Mean = {mean:.2f},  Std. Dev = {std:.2f}'
        plt.title(title)
        plt.xlabel('Value')
        plt.ylabel('Density')

        # Show the plot
        plt.show()

    @staticmethod
    def histogram_kde(data: pd.Series, bins='auto', title='Histogram with Kernel Density Estimate (KDE)'):
        """
        Create a histogram for the given data to visually check for normal distribution.

        Args:
        data (array-like): The dataset for which the histogram is to be created.
        bins (int or sequence or str): Specification of bin sizes. Default is 'auto'.
        title (str): Title of the plot.

        Returns:
        matplotlib figure: A histogram for assessing normality.
        """
        # Convert data to a numpy array if it's not already
        data = np.asarray(data)

        # Generate histogram
        plt.figure(figsize=(10, 6))
        sns.histplot(data, bins=bins, kde=True, color='blue')

        plt.title(title)
        plt.xlabel('Value')
        plt.ylabel('Frequency')

        # Show the plot
        plt.show()
    
    @staticmethod
    def qq_plot(data:pd.Series, title='Q-Q Plot'):
        """
        Create a Q-Q plot for the given data comparing it against a normal distribution.

        Args:
        data (array-like): The dataset for which the Q-Q plot is to be created.
        title (str): Title of the plot.

        Returns:
        matplotlib figure: A Q-Q plot.
        """
        # Convert data to a numpy array if it's not already
        data = np.asarray(data)

        # Generate Q-Q plot
        plt.figure(figsize=(6, 6))
        stats.probplot(data, dist="norm", plot=plt)

        # Add title and labels
        plt.title(title)
        plt.xlabel('Theoretical Quantiles')
        plt.ylabel('Sample Quantiles')

        # Show the plot
        plt.show()
    
    
    # -- Heteroscedasticity -- 
    @staticmethod
    def breusch_pagan(x:np.array, y:np.array, significance_level:float=0.05):
        """
        Perform the Breusch-Pagan test for heteroscedasticity and return results with heteroscedasticity indication.

        Parameters:
        x (array-like): The independent variables (explanatory variables) of the regression model.
        y (array-like): The dependent variable (response variable) of the regression model.
        significance_level (float): The significance level for determining heteroscedasticity.

        Returns:
        A dictionary containing the test statistic, p-value, and heteroscedasticity indication.
        """

        # Add a constant to the independent variables matrix
        X = sm.add_constant(x)

        # Fit the regression model
        model = sm.OLS(y, X).fit()

        # Get the residuals
        residuals = model.resid

        # Perform the Breusch-Pagan test
        bp_test = het_breuschpagan(residuals, model.model.exog)

        # Extract the test statistic and p-value
        bp_test_statistic = bp_test[0]
        bp_test_pvalue = bp_test[1]

        # Prepare the results in a clean format
        output = {
            'Breusch-Pagan Test Statistic': bp_test_statistic,
            'p-value': bp_test_pvalue,
            'Heteroscedasticity': ''
        }

        # Determine heteroscedasticity based on the significance level and p-value
        heteroscedasticity = bp_test_pvalue < significance_level

        output['Heteroscedasticity'] = 'Present' if heteroscedasticity else 'Absent'

        return output

    @staticmethod
    def display_breusch_pagan_results(bp_results:dict, print_output:bool=True, to_html: bool = False):
        # Convert Breusch-Pagan results to DataFrame
        bp_data = []
        for ticker, values in bp_results.items():
            row = {
                'Ticker': ticker,
                'Breusch-Pagan Test Statistic': values['Breusch-Pagan Test Statistic'],
                'p-value': round(values['p-value'], 6),
                'Heteroscedasticity': values['Heteroscedasticity']
            }
            bp_data.append(row)

        bp_df = pd.DataFrame(bp_data)
        footnote = "** IF p-value < 0.05, then REJECT the Null Hypothesis of homoscedasticity (constant variance) in favor of heteroscedasticity (varying variance).\n"
        
        if to_html:
            # Convert DataFrame to HTML table and add explanation
            html_table = bp_df.to_html(index=False, border=1)
            html_explanation = f"<p>{footnote}</p>"
            html_output = f"<h2>Breusch Pagan Results</h2>\n{html_table}\n{html_explanation}"
            return html_output
        elif print_output:
            print(f"Breusch Pagan Results:\n{bp_df}\n{footnote}")
        else:
            return f"Breusch Pagan Results:\n{bp_df.to_string(index=False)}\n{footnote}"
        
    @staticmethod
    def white_test(x:np.array, y:np.array, significance_level:float=0.05):
        """
        Perform White's test for heteroscedasticity and return results with heteroscedasticity indication.

        Parameters:
        x (array-like): The independent variables (explanatory variables) of the regression model.
        y (array-like): The dependent variable (response variable) of the regression model.
        significance_level (float): The significance level for determining heteroscedasticity.

        Returns:
        A dictionary containing the test statistic, p-value, and heteroscedasticity indication.
        """

        # Add a constant to the independent variables matrix
        X = sm.add_constant(x)

        # Fit the regression model
        model = sm.OLS(y, X).fit()

        # Get the residuals and the squared residuals
        residuals = model.resid

        # Perform White's test
        white_test = het_white(residuals, model.model.exog)

        # Extract the test statistic and p-value
        white_test_statistic = white_test[0]
        white_test_pvalue = white_test[1]

        # Prepare the results in a clean format
        output = {
            'White Test Statistic': white_test_statistic,
            'p-value': white_test_pvalue,
            'Heteroscedasticity': ''
        }

        # Determine heteroscedasticity based on the significance level and p-value
        heteroscedasticity = white_test_pvalue < significance_level
        output['Heteroscedasticity'] = 'Present' if heteroscedasticity else 'Absent'

        return output

    @staticmethod
    def display_white_test_results(white_results:dict, print_output:bool=True, to_html: bool = False):
        # Convert White test results to DataFrame
        white_data = []
        for ticker, values in white_results.items():
            row = {
                'Ticker': ticker,
                'White Test Statistic': values['White Test Statistic'],
                'p-value': round(values['p-value'], 6),
                'Heteroscedasticity': values['Heteroscedasticity']
            }
            white_data.append(row)

        white_df = pd.DataFrame(white_data)
        footnote = "** IF p-value < 0.05, then REJECT the Null Hypothesis of homoscedasticity (constant variance) in favor of heteroscedasticity (varying variance).\n"

        if to_html:
            # Convert DataFrame to HTML table and add explanation
            html_table = white_df.to_html(index=False, border=1)
            html_explanation = f"<p>{footnote}</p>"
            html_output = f"<h2>White Test Results</h2>\n{html_table}\n{html_explanation}"
            return html_output
        elif print_output:
            print(f"White Test Results:\n{white_df}\n{footnote}")
        else:
            return f"White Test Results:\n{white_df.to_string(index=False)}\n{footnote}"

    # -- Granger Causality -- 
    @staticmethod
    def granger_causality(data:pd.DataFrame, max_lag:int, significance_level:float=0.05):
        """
        Perform Granger Causality test for each pair of variables in the DataFrame.

        Args:
        data (DataFrame): A pandas DataFrame where each column represents a time series.
        max_lag (int): The maximum number of lags to test for Granger causality.
        significance_level (float): The significance level for statistical testing.

        Returns:
        dict: A dictionary with tuple keys (variable1, variable2) and values as dictionaries containing test statistics, p-values, and Granger causality indication.
        """
        variables = data.columns
        granger_results = {}

        for var1 in variables:
            for var2 in variables:
                if var1 != var2:
                    test_result = grangercausalitytests(data[[var1, var2]], maxlag=max_lag)
                    p_values = [test_result[lag][0]['ssr_chi2test'][1] for lag in range(1, max_lag + 1)]
                    min_p_value = min(p_values)
                    granger_results[(var1, var2)] = {
                        'min_p_value': min_p_value,
                        'Granger Causality': min_p_value < significance_level,
                        'significance': significance_level
                    }

        return granger_results
    
    @staticmethod
    def display_granger_results(granger_results:dict, print_output:bool=True, to_html: bool = False):
        # Creating DataFrame from the results
        granger_df = pd.DataFrame([
            {
                'Variable Pair': f'{pair[0]} -> {pair[1]}',
                'Min p-value': details['min_p_value'],
                'Granger Causality': 'Yes' if details['Granger Causality'] else 'No',
                'Significance Level': details['significance']
            }
            for pair, details in granger_results.items()
        ])

        # Display the DataFrame
        output = f"Granger Causality Results: \n{granger_df}"
        footnote = "** IF p-value < significance level then REJECT the NUll and conclude that the lagged values of one time series can provide useful information for predicting the other time series. \n"

        if to_html:
            # Convert DataFrame to HTML table and add explanation
            html_table = granger_df.to_html(index=False, border=1)
            html_explanation = f"<p>{footnote}</p>"
            html_output = f"<h2>Granger Causality Results</h2>\n{html_table}\n{html_explanation}"
            return html_output
        elif print_output:
            print(f"Granger Causality Results:\n{granger_df}\n{footnote}")
        else:
            return f"Granger Causality Results:\n{granger_df.to_string(index=False)}\n{footnote}"
    
    
    # -- Historcal Nature --
    @staticmethod
    def hurst_exponent(series:np.array):
        lags = range(2, 100)
        tau = [np.sqrt(np.std(np.subtract(series[lag:], series[:-lag]))) for lag in lags]
        poly = np.polyfit(np.log(lags), np.log(tau), 1)
        return poly[0] * 2.0
    
    @staticmethod
    def half_life(Y: pd.Series, Y_lagged: pd.Series, include_constant: bool = True):
        """ 
        AR Model that calculates the expected half-life of a mean reverting time series.

        Parameters:
        Y (pd.Series): Dependent variable.
        Y_lagged (pd.Series): Lagged series of the dependent variable.
        include_constant (bool): Flag to include a constant term in the regression model.

        Returns:
        float: The half-life of mean reversion.
        pd.Series: Residuals from the regression model.
        """
        if include_constant:
            Y_lagged = sm.add_constant(Y_lagged)  # Add a constant term to the regression model

        model = sm.OLS(Y, Y_lagged).fit()  # Fit the AR(1) model
        phi = model.params[-1]  # Get the AR coefficient (last parameter)

        # Ensure phi is in the expected range for mean reversion
        if phi <= 0 or phi >= 1:
            raise ValueError("Phi is outside the expected range (0, 1). The time series may not be mean-reverting.")

        half_life = -np.log(2) / np.log(phi)  # Calculate the half-life of mean reversion
        residuals = model.resid  # Get the residuals

        return half_life, residuals
    
    # @staticmethod
    # def variance_test(series:pd.Series):
    #     vratio, pvalue, _, _ = vratiotest(series)
    #     print(f'Variance Ratio: {vratio}, p-value: {pvalue}')
        
    
    # -- VECM Model --
    @staticmethod
    def vecm_model(data:pd.DataFrame, coint_rank:int, k_ar_diff:int):
        # Estimate the VECM model
        model = VECM(data, k_ar_diff= k_ar_diff, coint_rank=coint_rank)
        fitted_model = model.fit()
        return fitted_model

    
    # -- Walkforward Analysis
    @staticmethod
    def split_data(data:pd.DataFrame,train_ratio=0.8):
        split_index = int(len(data) * train_ratio)
        train_data = data.iloc[:split_index]
        test_data = data.iloc[split_index:]
        return train_data, test_data
    

    # -- Forescast Metrics -- 
    @staticmethod
    def evaluate_forecast(actual:pd.DataFrame, forecast:pd.DataFrame, print_output:bool=True):
        """
        Evaluate the accuracy of forecasts.

        Args:
        actual (DataFrame or Series): The actual observed values.
        forecast (DataFrame or Series): The forecasted values.

        Returns:
        dict: A dictionary containing various forecast accuracy metrics.
        """
        if not isinstance(actual, (pd.Series, pd.DataFrame)):
            raise ValueError("Actual data must be a pandas Series or DataFrame.")
        if not isinstance(forecast, (pd.Series, pd.DataFrame)):
            raise ValueError("Forecast data must be a pandas Series or DataFrame.")

        # Ensure forecast and actual data have the same length
        if len(actual) != len(forecast):
            raise ValueError("Actual and forecast must have the same length.")
        
        for col in actual.columns:
            mae = mean_absolute_error(actual[col], forecast[col])
            mse = mean_squared_error(actual[col], forecast[col])
            rmse = np.sqrt(mse)

            # MAPE can be infinite or NaN if actual values contain 0. It's handled by catching the error.
            try:
                mape = np.mean(np.abs((actual[col] - forecast[col]) / actual[col])) * 100
            except ValueError:
                mape = np.nan

            data = {
                'MAE': mae,
                'MSE': mse,
                'RMSE': rmse,
                'MAPE': mape
            }
            output = pd.DataFrame([data], index=[col])

            if print_output:
                print(output)
            else:
                return output


    # -- Plots --
    @staticmethod
    def line_plot(x:pd.Series,y:pd.Series, title:str="Time Series Plot", x_label:str="Time",y_label:str="Value"):
        plt.figure(figsize=(10, 6))
        plt.plot(x, y, marker='o')
        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.grid(True)
        plt.show()

    @staticmethod
    def plot_forecast(actual:pd.DataFrame, forecast:pd.DataFrame):
        # Ensure actual_values and forecasted_values have the same columns
        if set(actual.columns) != set(forecast.columns):
            raise ValueError("Columns of actual_values and forecasted_values do not match")

        # Iterate over each column to create separate plots
        for column in actual.columns:
            fig, ax = plt.subplots(figsize=(12, 6))

            # Plot the actual values
            ax.plot(actual[column], label=f"{column} Actual", color='blue')

            # Plot the forecasted values
            if column in forecast.columns:
                ax.plot(forecast[column], label=f"{column} Forecast", color='red')

            # Add labels, legend, and grid
            ax.grid(True)
            ax.set_xlabel('Time')
            ax.set_ylabel('Value')
            ax.set_title(f'Actual vs. Forecast for {column}')
            ax.legend()

            # Customize x-axis labels for readability
            plt.xticks(rotation=45)

            # Show the plot
            plt.show()  
    
    @staticmethod
    def plot_price_and_spread(price_data:pd.DataFrame, spread:pd.Series, show_plot=True):
        """
        Plot multiple ticker data on the left y-axis and spread with mean and standard deviations on the right y-axis.
        
        Parameters:
            price_data (pd.DataFrame): DataFrame containing the data with timestamps as index and multiple ticker columns.
            spread (pd.Series): Series containing the spread data.
        """
        # Extract data from the DataFrame
        timestamps = price_data.index

        # Create a figure and primary axis for price data (left y-axis)
        fig, ax1 = plt.subplots(figsize=(12, 6))

        # Plot each ticker on the left y-axis
        colors = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black', 'orange']  # Extend this list as needed
        for i, ticker in enumerate(price_data.columns):
            color = colors[i % len(colors)]  # Cycle through colors
            ax1.plot(timestamps, price_data[ticker], label=ticker, color=color, linewidth=2)

        ax1.set_yscale('linear')
        ax1.set_ylabel('Price')
        ax1.legend(loc='upper left')

        # Calculate mean and standard deviations for spread
        spread_mean = spread.rolling(window=20).mean()  # Adjust the window size as needed
        spread_std_1 = spread.rolling(window=20).std()  # 1 standard deviation
        spread_std_2 = 2 * spread.rolling(window=20).std()  # 2 standard deviations

        # Create a secondary axis for the spread with mean and standard deviations (right y-axis)
        ax2 = ax1.twinx()

        # Plot Spread on the right y-axis
        ax2.plot(timestamps, spread, label='Spread', color='purple', linewidth=2)
        ax2.plot(timestamps, spread_mean, label='Mean', color='orange', linestyle='--')
        ax2.fill_between(timestamps, spread_mean - spread_std_1, spread_mean + spread_std_1, color='gray', alpha=0.2, label='1 Std Dev')
        ax2.fill_between(timestamps, spread_mean - spread_std_2, spread_mean + spread_std_2, color='gray', alpha=0.4, label='2 Std Dev')
        ax2.set_yscale('linear')
        ax2.set_ylabel('Spread and Statistics')
        ax2.legend(loc='upper right')

        # Add grid lines
        ax1.grid(True)

        # Format x-axis labels for better readability
        plt.xticks(rotation=45)
        plt.xlabel('Timestamp')

        # Title
        plt.title('Price Data, Spread, and Statistics Over Time')

        # Show the plot
        plt.tight_layout()
        
        if show_plot:
            plt.show()

    @staticmethod
    def plot_zscore(zscore_series:pd.Series, window=20):
        """
        Plot Z-score along with its mean and standard deviations (1 and 2) on the right y-axis.
        
        Parameters:
            zscore_series (pd.Series): Series containing the Z-score data.
            window (int): Rolling window size for calculating mean and standard deviations (default is 20).
        """
        # Create a figure and primary axis for Z-score (left y-axis)
        fig, ax1 = plt.subplots(figsize=(12, 6))

        # Plot Z-score on the left y-axis
        ax1.plot(zscore_series.index, zscore_series, label='Z-Score', color='blue', linewidth=2)

        ax1.set_yscale('linear')
        ax1.set_ylabel('Z-Score')
        ax1.legend(loc='upper left')

        # Calculate mean and standard deviations for Z-score
        zscore_mean = zscore_series.rolling(window=window).mean()
        zscore_std_1 = zscore_series.rolling(window=window).std()  # 1 standard deviation
        zscore_std_2 = 2 * zscore_series.rolling(window=window).std()  # 2 standard deviations

        # Create a secondary axis for mean and standard deviations (right y-axis)
        ax2 = ax1.twinx()

        # Plot mean and standard deviations on the right y-axis
        ax2.plot(zscore_series.index, zscore_mean, label='Mean', color='orange', linestyle='--')
        ax2.fill_between(zscore_series.index, zscore_mean - zscore_std_1, zscore_mean + zscore_std_1, color='gray', alpha=0.2, label='1 Std Dev')
        ax2.fill_between(zscore_series.index, zscore_mean - zscore_std_2, zscore_mean + zscore_std_2, color='gray', alpha=0.4, label='2 Std Dev')
        ax2.set_yscale('linear')
        ax2.set_ylabel('Statistics')
        ax2.legend(loc='upper right')

        # Add grid lines
        ax1.grid(True)

        # Format x-axis labels for better readability
        plt.xticks(rotation=45)
        plt.xlabel('Timestamp')

        # Title
        plt.title('Z-Score and Statistics Over Time')

        # Show the plot
        plt.tight_layout()
        plt.show()

    # @staticmethod
    # def plot_price_and_spread_w_signals(price_data: pd.DataFrame, spread: pd.Series, signals: list, split_date=None, show_plot=True):
    #     """
    #     Plot multiple ticker data on the left y-axis, spread with mean and standard deviations on the right y-axis,
    #     and trading signals as icons.
        
    #     Parameters:
    #         price_data (pd.DataFrame): DataFrame containing the data with timestamps as index and multiple ticker columns.
    #         spread (pd.Series): Series containing the spread data.
    #         signals (pd.DataFrame): DataFrame containing signal data with timestamps as index and 'signal' column indicating 'long' or 'short'.
    #     """
    #     # Extract data from the DataFrame
    #     timestamps = price_data.index

    #     # Create a figure and primary axis for price data (left y-axis)
    #     fig, ax1 = plt.subplots(figsize=(12, 6))

    #     # Plot each ticker on the left y-axis
    #     colors = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black', 'orange']  # Extend this list as needed
    #     for i, ticker in enumerate(price_data.columns):
    #         color = colors[i % len(colors)]  # Cycle through colors
    #         ax1.plot(timestamps, price_data[ticker], label=ticker, color=color, linewidth=2)

    #     ax1.set_yscale('linear')
    #     ax1.set_ylabel('Price')
    #     ax1.legend(loc='upper left')

    #     # Calculate mean and standard deviations for spread
    #     spread_mean = spread.rolling(window=20).mean()  # Adjust the window size as needed
    #     spread_std_1 = spread.rolling(window=20).std()  # 1 standard deviation
    #     spread_std_2 = 2 * spread.rolling(window=20).std()  # 2 standard deviations

    #     # Create a secondary axis for the spread with mean and standard deviations (right y-axis)
    #     ax2 = ax1.twinx()

    #     # Plot Spread on the right y-axis
    #     ax2.plot(timestamps, spread, label='Spread', color='purple', linewidth=2)
    #     ax2.plot(timestamps, spread_mean, label='Mean', color='orange', linestyle='--')
    #     ax2.fill_between(timestamps, spread_mean - spread_std_1, spread_mean + spread_std_1, color='gray', alpha=0.2, label='1 Std Dev')
    #     ax2.fill_between(timestamps, spread_mean - spread_std_2, spread_mean + spread_std_2, color='gray', alpha=0.4, label='2 Std Dev')
    #     ax2.set_yscale('linear')
    #     ax2.set_ylabel('Spread and Statistics')
    #     ax2.legend(loc='upper right')

    #     # Plot signals
    #     for signal in signals:
    #         ts = pd.to_datetime(signal['timestamp'])
    #         price = signal['price']
    #         action = signal['action']
    #         if action == 'long':
    #             marker = '^'
    #             color = 'lime'
    #         elif action == 'short':
    #             marker = 'v'
    #             color = 'red'
    #         else:
    #             # Default marker for undefined actions
    #             marker = 'o'
    #             color = 'gray'
    #         ax1.scatter(ts, price, marker=marker, color=color, s=100)

    #     # Draw a dashed vertical line to separate test and training data
    #     if split_date is not None:
    #         split_date = pd.to_datetime(split_date)
    #         ax1.axvline(x=split_date, color='black', linestyle='--', linewidth=1)

    #     # Add grid lines
    #     ax1.grid(True)

    #     # Format x-axis labels for better readability
    #     plt.xticks(rotation=45)
    #     plt.xlabel('Timestamp')

    #     # Title
    #     plt.title('Price Data, Spread, Statistics, and Trading Signals Over Time')

    #     # Show the plot
    #     plt.tight_layout()
        
    #     if show_plot:
    #         plt.show()

    # -- Synthentic Timeseries --
    @staticmethod
    def generate_mean_reverting_series(n=1000, mu=0, theta=0.1 , sigma=0.2, start_value=1):
        """
        Generate a mean-reverting time series using the Ornstein-Uhlenbeck process.

        Parameters:
        n (int): The number of observations in the time series.
        mu (float): The long-term mean value towards which the time series reverts.
        theta (float): The rate of reversion to the mean.
        sigma (float): The volatility of the process.
        start_value (float): The starting value of the time series.

        Returns:
        np.array: A numpy array representing the generated time series.
        """
        time_series = [start_value]
        for _ in range(1, n):
            dt = 1  # Time step
            previous_value = time_series[-1]
            random_term = np.random.normal(loc=0.0, scale=np.sqrt(dt) * sigma)
            next_value = previous_value + theta * (mu - previous_value) * dt + random_term
            time_series.append(next_value)

        return np.array(time_series)

    @staticmethod
    def generate_trending_series(n=1000, start_value=0, trend=0.1, step_std=1):
        """
        Generate a trending time series.

        Parameters:
        n (int): The number of observations in the time series.
        start_value (float): The starting value of the time series.
        trend (float): The constant amount added to each step to create a trend.
        step_std (float): The standard deviation of the step size.

        Returns:
        np.array: A numpy array representing the generated time series.
        """
        time_series = [start_value]
        for _ in range(1, n):
            step = np.random.normal(scale=step_std) + trend
            next_value = time_series[-1] + step
            time_series.append(next_value)

        return np.array(time_series)

    @staticmethod
    def generate_random_walk_series(n=1000, start_value=0, step_std=1):
        """
        Generate a random walk time series.

        Parameters:
        n (int): The number of observations in the time series.
        start_value (float): The starting value of the time series.
        step_std (float): The standard deviation of the step size.

        Returns:
        np.array: A numpy array representing the generated time series.
        """
        time_series = [start_value]
        for _ in range(1, n):
            step = np.random.normal(scale=step_std)
            next_value = time_series[-1] + step
            time_series.append(next_value)

        return np.array(time_series)
      