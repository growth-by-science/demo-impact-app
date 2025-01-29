import streamlit as st
import plotly.graph_objects as go
import numpy as np
from src.ui.components import setup_page_config
from src.simulation.roic import (
    simulate_roic_improvement_scenarios,
    calculate_effective_tax_rate,
    simulate_multi_year_cumulative_roic
)

def create_roic_improvement_plot(scenarios, dark_mode=True):
    """Create plot showing ROIC improvement as ineffective spend is removed."""
    
    # Set colors based on theme
    bg_color = "#0E1117" if dark_mode else "white"
    grid_color = "#333" if dark_mode else "#E5E5E5"
    text_color = "white" if dark_mode else "black"
    
    # Colors for different scenarios
    colors = {
        0.25: '#007AFF',  # Blue
        0.50: '#5856D6',  # Purple
        0.75: '#AF52DE'   # Pink
    }
    
    fig = go.Figure()
    
    # Calculate min and max ROIC values for y-axis range
    min_roic = float('inf')
    max_roic = float('-inf')
    for _, (_, roic_vals) in scenarios.items():
        roic_percentages = [r * 100 for r in roic_vals]
        min_roic = min(min_roic, min(roic_percentages))
        max_roic = max(max_roic, max(roic_percentages))
    
    # Add padding to min and max
    padding = (max_roic - min_roic) * 0.1  # 10% of the range
    min_roic = min_roic - padding
    max_roic = max(max_roic + padding, 40)  # Ensure max is at least 40% for reference lines
    
    # Add company reference lines
    companies = {
        'META': 35,
        'AAPL': 39,
        'NFLX': 23
    }
    
    for company, roic in companies.items():
        # Add the reference line
        fig.add_trace(go.Scatter(
            x=[0, 1],  # Full width of the plot
            y=[roic, roic],
            mode='lines',
            name=f'{company} ({roic}%)',
            line=dict(
                color='#FFD700',  # Gold color for reference lines
                width=1,
                dash='dash'
            ),
            showlegend=False,  # Hide from legend
            hovertemplate=f'{company}: {roic}% ROIC<extra></extra>'
        ))
        
        # Add the label on the line
        fig.add_annotation(
            x=0.95,  # Place label near the right end but not at the edge
            y=roic,
            text=company,
            xanchor='right',
            yanchor='middle',
            showarrow=False,
            font=dict(
                color='#FFD700',
                size=12
            ),
            bgcolor=bg_color,  # Match plot background
            borderpad=2  # Add some padding around text
        )
    
    # Add a line for each scenario
    for effectiveness, (removal_pcts, roic_vals) in scenarios.items():
        fig.add_trace(go.Scatter(
            x=removal_pcts,
            y=[r * 100 for r in roic_vals],
            mode='lines',
            name=f'{effectiveness*100:.0f}% Effective',
            line=dict(
                color=colors[effectiveness],
                width=3
            )
        ))
    
    # Update layout
    fig.update_layout(
        title=dict(
            text='ROIC Improvement from Removing Ineffective Spend',
            x=0.5,
            y=0.95,
            xanchor='center',
            yanchor='top',
            font=dict(size=20, color=text_color)
        ),
        xaxis=dict(
            title='Ineffective Spend Removed (%)',
            tickformat=',.0%',
            gridcolor=grid_color,
            showgrid=True,
            color=text_color
        ),
        yaxis=dict(
            title='ROIC (%)',
            tickformat=',.1f',
            gridcolor=grid_color,
            showgrid=True,
            zeroline=True,
            zerolinecolor=grid_color,
            color=text_color,
            range=[min_roic, max_roic],  # Set range to include negative values with padding
            autorange=False  # Disable autorange to enforce our custom range
        ),
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            font=dict(color=text_color),
            bgcolor='rgba(0,0,0,0)'
        ),
        hovermode='x unified',
        margin=dict(t=50)
    )
    
    return fig

def create_tax_rate_plot(waste_percentages, effective_tax_rates, base_tax_rate, dark_mode=True):
    """Create plot showing effective tax rate."""
    
    # Set colors based on theme
    bg_color = "#0E1117" if dark_mode else "white"
    grid_color = "#333" if dark_mode else "#E5E5E5"
    text_color = "white" if dark_mode else "black"
    
    fig = go.Figure()
    
    # Calculate max tax rate for y-axis range
    max_tax_rate = max(r * 100 for r in effective_tax_rates)
    
    # Add effective tax rate line
    fig.add_trace(go.Scatter(
        x=waste_percentages,
        y=[r * 100 for r in effective_tax_rates],
        mode='lines',
        name='True Tax Rate',
        line=dict(color='#FF3B30', width=3)
    ))
    
    # Update layout
    fig.update_layout(
        title=dict(
            text='True Tax Rate From Ineffective Marketing Spend',
            x=0.5,
            y=0.95,
            xanchor='center',
            yanchor='top',
            font=dict(size=20, color=text_color)
        ),
        xaxis=dict(
            title='Ineffective Marketing %',
            tickformat=',.0%',
            gridcolor=grid_color,
            showgrid=True,
            color=text_color
        ),
        yaxis=dict(
            title='Tax Rate (%)',
            tickformat=',.1f',
            gridcolor=grid_color,
            showgrid=True,
            zeroline=True,
            zerolinecolor=grid_color,
            color=text_color,
            range=[0, max_tax_rate * 1.1]  # Start at 0, add 10% padding at top
        ),
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            font=dict(color=text_color),
            bgcolor='rgba(0,0,0,0)'
        ),
        hovermode='x unified',
        margin=dict(t=50)
    )
    
    return fig

def create_cumulative_roic_plot(scenarios, dark_mode=True):
    """Create plot showing cumulative ROIC over time for different waste removal scenarios."""
    
    # Set colors based on theme
    bg_color = "#0E1117" if dark_mode else "white"
    grid_color = "#333" if dark_mode else "#E5E5E5"
    text_color = "white" if dark_mode else "black"
    
    # Colors for different scenarios
    colors = {
        0.0: '#FF3B30',   # Red (no removal)
        0.33: '#FF9500',  # Orange (33% removal)
        0.66: '#34C759',  # Green (66% removal)
        0.99: '#007AFF'   # Blue (99% removal)
    }
    
    fig = go.Figure()
    
    # Calculate max ROIC value for y-axis range
    max_roic = 0
    for removal_pct, (years, mean_roic, std_roic) in scenarios.items():
        max_roic = max(max_roic, np.max((mean_roic + std_roic) * 100))
    
    # Add a line for each scenario
    for removal_pct, (years, mean_roic, std_roic) in scenarios.items():
        # Add confidence band (without legend entry)
        fig.add_trace(go.Scatter(
            x=years + years[::-1],
            y=[(mean_roic[i] + std_roic[i]) * 100 for i in range(len(years))] + 
              [(mean_roic[i] - std_roic[i]) * 100 for i in range(len(years)-1, -1, -1)],
            fill='toself',
            fillcolor=f'rgba{tuple(list(int(colors[removal_pct].lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + [0.2])}',
            line=dict(color='rgba(255,255,255,0)'),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Add mean line (with legend entry)
        fig.add_trace(go.Scatter(
            x=years,
            y=[val * 100 for val in mean_roic],
            mode='lines',
            name=f'{removal_pct*100:.0f}% Waste Removed',
            line=dict(
                color=colors[removal_pct],
                width=3
            )
        ))
    
    # Update layout
    fig.update_layout(
        title=dict(
            text='5-Year Cumulative ROIC by Waste Removal Scenario',
            x=0.5,
            y=0.95,
            xanchor='center',
            yanchor='top',
            font=dict(size=20, color=text_color)
        ),
        xaxis=dict(
            title='Year',
            gridcolor=grid_color,
            showgrid=True,
            color=text_color,
            dtick=1  # Show every year
        ),
        yaxis=dict(
            title='Cumulative ROIC (%)',
            tickformat=',.1f',
            gridcolor=grid_color,
            showgrid=True,
            zeroline=True,
            zerolinecolor=grid_color,
            color=text_color,
            range=[0, max_roic * 1.1]  # Start at 0, add 10% padding at top
        ),
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            font=dict(color=text_color),
            bgcolor='rgba(0,0,0,0)'
        ),
        hovermode='x unified',
        margin=dict(t=50),
        height=500  # Make the plot taller
    )
    
    return fig

def main():
    # Set up page configuration
    setup_page_config()
    
    # Add the fixed button styling first
    st.markdown(
        """
        <style>
        .fixed-button {
            position: fixed;
            left: 1rem;
            bottom: 1rem;
            width: 306px;
            z-index: 1000;
            background-color: #0E1117;
            padding: 1rem;
            border-radius: 0.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Create a container for the floating Run Analysis button
    st.markdown('<div class="fixed-button">', unsafe_allow_html=True)
    run_simulation = st.button("Run Analysis", type="primary")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Create two columns: sidebar for inputs and main area for graphs
    with st.sidebar:
        st.title("Business Metrics")
        
        # Input fields (all values in millions)
        revenue = st.number_input(
            "Annual Revenue ($M)",
            min_value=0.0,
            value=100.0,  # $100M default
            step=5.0,
            help="Annual revenue in millions of dollars"
        ) * 1_000_000

        cogs = st.number_input(
            "Cost of Goods Sold ($M)",
            min_value=0.0,
            value=40.0,  # $40M default
            step=2.5,
            help="Annual cost of goods sold in millions of dollars"
        ) * 1_000_000

        non_marketing_opex = st.number_input(
            "Non-Marketing Operating Expenses ($M)",
            min_value=0.0,
            value=20.0,  # $20M default
            step=1.0,
            help="Annual operating expenses excluding marketing in millions of dollars"
        ) * 1_000_000

        total_marketing_spend = st.number_input(
            "Total Marketing Spend ($M)",
            min_value=0.0,
            value=30.0,  # $30M default
            step=0.5,
            help="Annual marketing budget in millions of dollars"
        ) * 1_000_000

        tax_rate = st.slider(
            "Tax Rate (%)",
            min_value=0.0,
            max_value=100.0,
            value=25.0,
            step=1.0,
            help="Effective tax rate as a percentage"
        ) / 100

        invested_capital = st.number_input(
            "Invested Capital ($M)",
            min_value=0.0,
            value=70.0,  # $70M default
            step=5.0,
            help="Total invested capital in millions of dollars"
        ) * 1_000_000
        
        st.divider()
        st.subheader("Growth Parameters")
        
        marketing_growth = st.slider(
            "Marketing Spend Growth (%/year)",
            min_value=0.0,
            max_value=50.0,
            value=10.0,
            step=1.0,
            help="Annual growth rate of marketing spend"
        ) / 100
        
        capital_growth = st.slider(
            "Invested Capital Growth (%/year)",
            min_value=0.0,
            max_value=50.0,
            value=10.0,  # Updated to 10%
            step=1.0,
            help="Annual growth rate of invested capital"
        ) / 100
        
        # Add simulation parameters
        st.divider()
        n_simulations = st.number_input("Number of Simulations", min_value=100, value=1000, step=100)

    # Main area for graphs
    st.title("Marketing Efficiency Impact on ROIC")

    if run_simulation:
        with st.spinner("Running analysis..."):
            # First two plots
            improvement_scenarios = simulate_roic_improvement_scenarios(
                revenue=revenue,
                cogs=cogs,
                non_marketing_opex=non_marketing_opex,
                total_marketing_spend=total_marketing_spend,
                tax_rate=tax_rate,
                invested_capital=invested_capital,
                removal_points=50
            )
            
            # Calculate effective tax rates directly
            waste_points = 50
            waste_percentages = np.linspace(0, 1, waste_points)
            effective_tax_rates = []
            
            for waste in waste_percentages:
                eff_rate = calculate_effective_tax_rate(
                    revenue=revenue,
                    cogs=cogs,
                    non_marketing_opex=non_marketing_opex,
                    total_marketing_spend=total_marketing_spend,
                    waste_percentage=waste,
                    tax_rate=tax_rate
                )
                effective_tax_rates.append(eff_rate)
            
            # Create tabs for different analyses
            tab1, tab2 = st.tabs(["Single-Year Analysis", "Multi-Year Simulation"])
            
            # Single-Year Analysis Tab
            with tab1:
                col1, col2 = st.columns(2)
                
                with col1:
                    roic_fig = create_roic_improvement_plot(
                        improvement_scenarios,
                        dark_mode=True
                    )
                    st.plotly_chart(roic_fig, use_container_width=True)
                
                with col2:
                    tax_fig = create_tax_rate_plot(
                        waste_percentages,
                        effective_tax_rates,
                        tax_rate,
                        dark_mode=True
                    )
                    st.plotly_chart(tax_fig, use_container_width=True)
            
            # Multi-Year Analysis Tab
            with tab2:
                st.caption("Showing impact of waste removal on 5-year cumulative ROIC, assuming 50% of initial marketing spend is effective")
                
                cumulative_scenarios = simulate_multi_year_cumulative_roic(
                    revenue=revenue,
                    cogs=cogs,
                    non_marketing_opex=non_marketing_opex,
                    total_marketing_spend=total_marketing_spend,
                    tax_rate=tax_rate,
                    invested_capital=invested_capital,
                    marketing_growth=marketing_growth,
                    capital_growth=capital_growth,
                    n_simulations=n_simulations
                )
                
                cumulative_fig = create_cumulative_roic_plot(
                    cumulative_scenarios,
                    dark_mode=True
                )
                st.plotly_chart(cumulative_fig, use_container_width=True)
    else:
        st.info("Click 'Run Analysis' to start the analysis.")

if __name__ == "__main__":
    main() 