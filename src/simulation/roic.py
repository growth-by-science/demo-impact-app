import numpy as np
from typing import Tuple, Dict

def calculate_effective_tax_rate(
    revenue: float,
    cogs: float,
    non_marketing_opex: float,
    total_marketing_spend: float,
    waste_percentage: float,
    tax_rate: float
) -> float:
    """
    Calculate the effective tax rate that would result in the same NOPAT when applied to true operating income.
    The true operating income is what we would have without waste, but we're getting the same NOPAT as if
    we had the waste, which means our effective tax rate must be higher.
    """
    effective_marketing = total_marketing_spend * (1 - waste_percentage)
    wasted_marketing = total_marketing_spend * waste_percentage
    
    # True operating income (without waste)
    true_operating_income = revenue - cogs - non_marketing_opex - effective_marketing
    
    if true_operating_income <= 0:
        return 0.0
    
    # NOPAT with waste (this is what we actually get)
    actual_operating_income = true_operating_income - wasted_marketing
    actual_nopat = actual_operating_income * (1 - tax_rate)
    
    # Solve for effective tax rate that gives same NOPAT when applied to true operating income
    # actual_nopat = true_operating_income * (1 - effective_tax_rate)
    effective_tax_rate = 1 - (actual_nopat / true_operating_income)
    
    return effective_tax_rate

def calculate_roic_improvement(
    revenue: float,
    cogs: float,
    non_marketing_opex: float,
    total_marketing_spend: float,
    effectiveness_percentage: float,  # How much of spend IS effective (0.25, 0.50, 0.75)
    tax_rate: float,
    invested_capital: float,
    removal_points: int = 50
) -> Tuple[list, list]:
    """
    Calculate ROIC as ineffective spend is removed.
    
    Args:
        effectiveness_percentage: Percentage of marketing spend that IS effective (0.25, 0.50, 0.75)
        removal_points: Number of points to calculate for smooth line
        
    Returns:
        Tuple containing:
        - removal percentages (0-100%)
        - ROIC values at each removal percentage
    """
    removal_percentages = np.linspace(0, 1, removal_points)
    roic_values = []
    
    # Split marketing spend into effective and ineffective portions
    effective_spend = total_marketing_spend * effectiveness_percentage
    ineffective_spend = total_marketing_spend * (1 - effectiveness_percentage)
    
    for removal_pct in removal_percentages:
        # Calculate how much ineffective spend we're removing
        spend_removed = ineffective_spend * removal_pct
        current_marketing_spend = total_marketing_spend - spend_removed
        
        # Calculate operating income with reduced marketing spend
        operating_income = revenue - cogs - non_marketing_opex - current_marketing_spend
        
        if operating_income <= 0 or invested_capital <= 0:
            roic_values.append(0.0)
            continue
        
        # Calculate NOPAT using base tax rate
        nopat = operating_income * (1 - tax_rate)
        roic = nopat / invested_capital
        roic_values.append(roic)
    
    return removal_percentages.tolist(), roic_values

def simulate_roic_improvement_scenarios(
    revenue: float,
    cogs: float,
    non_marketing_opex: float,
    total_marketing_spend: float,
    tax_rate: float,
    invested_capital: float,
    removal_points: int = 50
) -> Dict[float, Tuple[list, list]]:
    """
    Calculate ROIC improvement for different effectiveness scenarios.
    
    Returns:
        Dictionary with effectiveness percentages as keys (0.25, 0.50, 0.75)
        and tuples of (removal_percentages, roic_values) as values
    """
    effectiveness_scenarios = {0.25: None, 0.50: None, 0.75: None}
    
    for effectiveness in effectiveness_scenarios.keys():
        removal_pcts, roic_vals = calculate_roic_improvement(
            revenue=revenue,
            cogs=cogs,
            non_marketing_opex=non_marketing_opex,
            total_marketing_spend=total_marketing_spend,
            effectiveness_percentage=effectiveness,
            tax_rate=tax_rate,
            invested_capital=invested_capital,
            removal_points=removal_points
        )
        effectiveness_scenarios[effectiveness] = (removal_pcts, roic_vals)
    
    return effectiveness_scenarios

def simulate_multi_year_cumulative_roic(
    # Initial conditions
    revenue: float,
    cogs: float,
    non_marketing_opex: float,
    total_marketing_spend: float,
    tax_rate: float,
    invested_capital: float,
    # Growth rates
    marketing_growth: float,  # Base marketing growth rate
    capital_growth: float,
    # Simulation parameters
    n_years: int = 5,
    n_simulations: int = 1000,
    base_effectiveness: float = 0.5,  # 50% of spend is effective by default
    removal_scenarios: list = [0.0, 0.33, 0.66, 0.99]  # % of waste removed
) -> Dict[float, Tuple[list, list, list]]:
    """
    Simulate cumulative ROIC over multiple years with different waste removal scenarios.
    
    Args:
        base_effectiveness: Percentage of marketing spend that is effective (default 0.5)
        removal_scenarios: List of percentages of waste to remove
        
    Returns:
        Dictionary with removal percentages as keys and tuples of:
        - years
        - mean cumulative ROIC values
        - std dev of cumulative ROIC values
    """
    years = list(range(1, n_years + 1))
    scenarios = {removal: None for removal in removal_scenarios}
    
    # Stochastic parameters
    revenue_std = 0.05  # Standard deviation for revenue growth variation
    roic_impact = 1.0  # How much ROIC impacts marketing growth
    
    for removal_pct in removal_scenarios:
        all_cumulative_roics = []
        
        for _ in range(n_simulations):
            yearly_nopat = []
            yearly_capital = []
            
            # Initialize tracking variables
            current_revenue = revenue
            current_marketing = total_marketing_spend
            current_capital = invested_capital
            prior_year_roic = 0.0
            
            for year in range(n_years):
                # Calculate marketing spend after waste removal
                if year == 0:
                    # First year: remove waste from entire marketing spend
                    waste_amount = current_marketing * (1 - base_effectiveness)
                    removed_waste = waste_amount * removal_pct
                    current_marketing = current_marketing - removed_waste  # Reduce marketing spend by removed waste
                else:
                    # Adjust growth rate based on prior year's ROIC performance
                    roic_adjustment = (prior_year_roic - 0.05) * roic_impact  # Compare to 5% baseline ROIC
                    adjusted_growth = marketing_growth + max(-0.1, min(0.2, roic_adjustment))
                    
                    # For subsequent years, apply waste removal to the growth portion
                    base_growth = current_marketing * adjusted_growth
                    waste_in_growth = base_growth * (1 - base_effectiveness)
                    removed_growth_waste = waste_in_growth * removal_pct
                    actual_growth = base_growth - removed_growth_waste
                    current_marketing += actual_growth
                
                # Calculate operating income and NOPAT
                operating_income = (
                    current_revenue 
                    - cogs  # COGS held constant
                    - non_marketing_opex  # Non-marketing OpEx held constant
                    - current_marketing  # Using reduced marketing spend
                )
                
                nopat = max(0, operating_income * (1 - tax_rate))
                
                # Store results for this year
                yearly_nopat.append(nopat)
                yearly_capital.append(current_capital)
                
                # Calculate single-year ROIC for growth calculations
                current_roic = nopat / current_capital if current_capital > 0 else 0
                
                if year < n_years - 1:  # Don't update for the last year
                    # Grow revenue based on current marketing spend
                    # More marketing spend = more revenue growth, but with diminishing returns
                    base_revenue_growth = marketing_growth * (current_marketing / total_marketing_spend) ** 0.7
                    
                    # Add ROIC performance boost to revenue growth
                    roic_boost = max(0, (current_roic - 0.05) * 0.7)  # Additional growth for above-baseline ROIC
                    total_revenue_growth = base_revenue_growth + roic_boost
                    
                    # Add random variation
                    revenue_growth = np.random.normal(total_revenue_growth, revenue_std)
                    current_revenue *= (1 + max(0, revenue_growth))
                    
                    # Grow invested capital at user-specified rate
                    current_capital *= (1 + capital_growth)
                    
                    # Store ROIC for next iteration
                    prior_year_roic = current_roic
            
            # Calculate cumulative ROIC for each year
            cumulative_nopats = np.cumsum(yearly_nopat)
            cumulative_capitals = np.cumsum(yearly_capital)
            yearly_cumulative_roics = cumulative_nopats / cumulative_capitals
            all_cumulative_roics.append(yearly_cumulative_roics)
        
        # Calculate statistics across simulations for each year
        all_cumulative_roics = np.array(all_cumulative_roics)
        mean_roics = np.mean(all_cumulative_roics, axis=0)
        std_roics = np.std(all_cumulative_roics, axis=0)
        
        scenarios[removal_pct] = (years, mean_roics, std_roics)
    
    return scenarios
