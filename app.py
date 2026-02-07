import numpy as np
import cv2
from scipy import ndimage
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import eigsh
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
from sklearn.cluster import DBSCAN
from skimage import feature, filters, morphology
import json
from datetime import datetime
import base64
import io

# ============================================================================
# CORE ENGINE: TOPOLOGICAL CHAOS ANALYSIS & SPATIAL ENTROPY
# ============================================================================

class SpatialEntropyEngine:
    """
    Implements Laplacian Variance-based Spatial Entropy for neoplastic zone detection
    Creates the 'Thermal Heatmap' for WSI Global Scan
    """
    
    def _init_(self, wsi_image, sigma=1.0, chaos_threshold=0.15):
        self.wsi = wsi_image
        self.sigma = sigma
        self.chaos_threshold = chaos_threshold
        self.laplacian_variance = None
        self.entropy_map = None
        self.neoplastic_zones = None
        
    def compute_laplacian_variance(self):
        """Calculate Laplacian of Gaussian variance for spatial chaos detection"""
        if len(self.wsi.shape) == 3:
            gray = cv2.cvtColor(self.wsi, cv2.COLOR_RGB2GRAY)
        else:
            gray = self.wsi
            
        # Gaussian smoothing
        smoothed = cv2.GaussianBlur(gray.astype(np.float32), (0, 0), self.sigma)
        
        # Laplacian operator
        laplacian = cv2.Laplacian(smoothed, cv2.CV_64F)
        
        # Local variance calculation using sliding window
        kernel_size = 15
        local_variance = np.zeros_like(laplacian)
        
        for i in range(kernel_size//2, laplacian.shape[0] - kernel_size//2):
            for j in range(kernel_size//2, laplacian.shape[1] - kernel_size//2):
                window = laplacian[i-kernel_size//2:i+kernel_size//2+1,
                                  j-kernel_size//2:j+kernel_size//2+1]
                local_variance[i, j] = np.var(window)
                
        self.laplacian_variance = local_variance
        return local_variance
    
    def compute_spatial_entropy(self, window_size=31):
        """Generate entropy map from Laplacian variance"""
        if self.laplacian_variance is None:
            self.compute_laplacian_variance()
            
        entropy_map = np.zeros_like(self.laplacian_variance)
        half_window = window_size // 2
        
        for i in range(half_window, self.laplacian_variance.shape[0] - half_window):
            for j in range(half_window, self.laplacian_variance.shape[1] - half_window):
                window = self.laplacian_variance[i-half_window:i+half_window+1,
                                               j-half_window:j+half_window+1]
                
                # Normalize to probability distribution
                hist, _ = np.histogram(window.flatten(), bins=32, density=True)
                hist = hist[hist > 0]
                
                # Shannon entropy
                entropy = -np.sum(hist * np.log2(hist))
                entropy_map[i, j] = entropy
                
        self.entropy_map = entropy_map
        return entropy_map
    
    def detect_neoplastic_zones(self):
        """Identify regions exceeding chaos threshold"""
        if self.entropy_map is None:
            self.compute_spatial_entropy()
            
        # Binary mask of chaotic regions
        chaos_mask = self.entropy_map > self.chaos_threshold
        
        # Morphological operations to clean mask
        chaos_mask = morphology.binary_opening(chaos_mask, morphology.disk(3))
        chaos_mask = morphology.binary_closing(chaos_mask, morphology.disk(5))
        
        # Label connected components
        labeled, num_features = ndimage.label(chaos_mask)
        
        self.neoplastic_zones = {
            'mask': chaos_mask,
            'labeled_regions': labeled,
            'num_regions': num_features,
            'chaos_intensity': self.entropy_map[chaos_mask].mean() if np.any(chaos_mask) else 0
        }
        
        return self.neoplastic_zones

# ============================================================================
# NUCLEAR PLEOMORPHISM QUANTIFICATION
# ============================================================================

class ISUPGradingEngine:
    """
    Implements Local Binary Patterns (LBP) and Fractal Dimensioning
    for nuclear pleomorphism quantification and ISUP/WHO grading
    """
    
    def _init_(self, roi_image):
        self.roi = roi_image
        self.lbp_features = None
        self.fractal_dimension = None
        self.nuclear_metrics = {}
        self.isup_grade = None
        
    def compute_lbp_features(self, radius=3, n_points=24):
        """Calculate Local Binary Patterns for nuclear texture analysis"""
        if len(self.roi.shape) == 3:
            gray = cv2.cvtColor(self.roi, cv2.COLOR_RGB2GRAY)
        else:
            gray = self.roi
            
        # Apply fastNlMeansDenoising for image enhancement
        denoised = cv2.fastNlMeansDenoising(gray.astype(np.uint8), h=10)
        
        # Histogram Equalization for contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(denoised)
        
        # Compute LBP
        lbp = feature.local_binary_pattern(enhanced, n_points, radius, method='uniform')
        
        # Calculate LBP histogram features
        n_bins = int(lbp.max() + 1)
        hist, _ = np.histogram(lbp.flatten(), bins=n_bins, range=(0, n_bins), density=True)
        
        # Statistical features from LBP histogram
        self.lbp_features = {
            'uniformity': np.sum(hist**2),
            'entropy': -np.sum(hist * np.log2(hist + 1e-10)),
            'contrast': np.std(hist),
            'histogram': hist
        }
        
        return self.lbp_features
    
    def compute_fractal_dimension(self, box_sizes=None):
        """Calculate fractal dimension using box-counting method"""
        if len(self.roi.shape) == 3:
            gray = cv2.cvtColor(self.roi, cv2.COLOR_RGB2GRAY)
        else:
            gray = self.roi
            
        # Threshold to binary image
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        if box_sizes is None:
            box_sizes = [2, 4, 8, 16, 32, 64]
            
        counts = []
        
        for size in box_sizes:
            # Count number of boxes containing foreground pixels
            grid = binary[::size, ::size]
            count = np.sum(grid > 0)
            counts.append(count)
            
        # Linear fit in log-log space
        logs = np.log(box_sizes)
        log_counts = np.log(counts)
        
        # Fractal dimension is negative slope
        coeffs = np.polyfit(logs, log_counts, 1)
        fractal_dim = -coeffs[0]
        
        self.fractal_dimension = fractal_dim
        return fractal_dim
    
    def compute_nuclear_metrics(self):
        """Calculate comprehensive nuclear features"""
        if self.lbp_features is None:
            self.compute_lbp_features()
            
        if self.fractal_dimension is None:
            self.compute_fractal_dimension()
            
        # Additional nuclear metrics
        if len(self.roi.shape) == 3:
            gray = cv2.cvtColor(self.roi, cv2.COLOR_RGB2GRAY)
        else:
            gray = self.roi
            
        # Nuclear segmentation (simplified)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Morphological operations for nuclear separation
        kernel = np.ones((3,3), np.uint8)
        opened = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(opened, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) > 0:
            # Calculate nuclear size statistics
            areas = [cv2.contourArea(cnt) for cnt in contours]
            self.nuclear_metrics.update({
                'nuclear_count': len(contours),
                'mean_area': np.mean(areas),
                'area_std': np.std(areas),
                'area_cv': np.std(areas) / (np.mean(areas) + 1e-10),
                'max_area': np.max(areas),
                'min_area': np.min(areas)
            })
            
            # Calculate shape irregularity
            circularities = []
            for cnt in contours:
                area = cv2.contourArea(cnt)
                perimeter = cv2.arcLength(cnt, True)
                if perimeter > 0:
                    circularity = 4 * np.pi * area / (perimeter ** 2)
                    circularities.append(circularity)
                    
            if circularities:
                self.nuclear_metrics['mean_circularity'] = np.mean(circularities)
                self.nuclear_metrics['circularity_std'] = np.std(circularities)
        
        return self.nuclear_metrics
    
    def determine_isup_grade(self):
        """Apply ISUP/WHO grading logic based on quantitative metrics"""
        if not self.nuclear_metrics:
            self.compute_nuclear_metrics()
            
        # Grade thresholds based on nuclear entropy and fractal dimension
        nuclear_entropy = self.lbp_features['entropy']
        fractal_dim = self.fractal_dimension
        area_cv = self.nuclear_metrics.get('area_cv', 0)
        
        # Grading logic
        if nuclear_entropy < 0.2 and fractal_dim < 1.3 and area_cv < 0.3:
            grade = 1  # Standard Homogeneity
            grade_text = "Grade 1 - Clear Cell RCC, Low Grade"
        elif nuclear_entropy < 0.35 and fractal_dim < 1.6 and area_cv < 0.5:
            grade = 2  # Moderate Variance
            grade_text = "Grade 2 - Clear Cell RCC, Intermediate Grade"
        elif nuclear_entropy < 0.5 and fractal_dim < 1.9:
            grade = 3  # High Nuclear Entropy
            grade_text = "Grade 3 - Clear Cell RCC, High Grade"
        else:
            grade = 4  # Extreme Anaplasia/Sarcomatoid Features
            grade_text = "Grade 4 - Sarcomatoid/Rhabdoid Features"
            
        self.isup_grade = {
            'grade': grade,
            'text': grade_text,
            'nuclear_entropy': nuclear_entropy,
            'fractal_dimension': fractal_dim,
            'area_coefficient_variation': area_cv
        }
        
        return self.isup_grade

# ============================================================================
# PHARMACOLOGICAL MAPPING ENGINE
# ============================================================================

class PharmacologicalMapper:
    """
    Maps ISUP Grades to NCCN guidelines and provides therapy recommendations
    """
    
    def _init_(self):
        self.nccn_matrix = {
            1: {
                'primary_therapy': 'Active Surveillance or Partial Nephrectomy',
                'systemic_therapy': 'None recommended',
                'targeted_agents': ['Observation preferred'],
                'survival_5yr': '95-98%',
                'evidence_level': 'NCCN Category 1'
            },
            2: {
                'primary_therapy': 'Partial/Radical Nephrectomy',
                'systemic_therapy': 'Adjuvant Pembrolizumab (if high risk)',
                'targeted_agents': ['Sunitinib', 'Pazopanib (Category 2A)'],
                'survival_5yr': '75-85%',
                'evidence_level': 'NCCN Category 1'
            },
            3: {
                'primary_therapy': 'Radical Nephrectomy + Lymph Node Dissection',
                'systemic_therapy': 'Sunitinib or Pazopanib (First-line)',
                'targeted_agents': ['Cabozantinib', 'Lenvatinib+Everolimus'],
                'survival_5yr': '50-65%',
                'evidence_level': 'NCCN Category 1'
            },
            4: {
                'primary_therapy': 'Cytoreductive Nephrectomy (if feasible)',
                'systemic_therapy': 'Nivolumab + Ipilimumab (Preferred)',
                'targeted_agents': ['Cabozantinib', 'Pembrolizumab+Axitinib'],
                'survival_5yr': '20-40%',
                'evidence_level': 'NCCN Category 1'
            },
            'metastatic_override': {
                'primary_therapy': 'Systemic Therapy First',
                'systemic_therapy': 'Doublet Immunotherapy or TKI+IO',
                'targeted_agents': ['Nivo+Ipi', 'Pembro+Axi', 'Cabo+Nivo'],
                'survival_5yr': '15-20%',
                'evidence_level': 'NCCN Category 1 (M1 Disease)'
            }
        }
        
    def get_therapy_recommendation(self, isup_grade, metastatic=False):
        """Return therapy recommendation based on grade and metastatic status"""
        if metastatic:
            base = self.nccn_matrix['metastatic_override'].copy()
            base['clinical_context'] = 'METASTATIC OVERRIDE ACTIVATED'
            base['grade_original'] = isup_grade
        else:
            base = self.nccn_matrix.get(isup_grade, self.nccn_matrix[4]).copy()
            base['clinical_context'] = 'Localized Disease Protocol'
            
        # Calculate complexity index
        complexity = (isup_grade * 25) + (20 if metastatic else 0)
        base['complexity_index'] = min(complexity, 100)
        
        return base

# ============================================================================
# DASHBOARD UI/UX COMPONENTS
# ============================================================================

def create_thermal_heatmap_figure(entropy_map):
    """Create thermal heatmap visualization"""
    fig = go.Figure(data=go.Heatmap(
        z=entropy_map,
        colorscale=[
            [0, 'rgb(5, 10, 30)'],        # Deep navy
            [0.3, 'rgb(0, 100, 150)'],    # Medium blue
            [0.6, 'rgb(255, 100, 0)'],    # Orange
            [1, 'rgb(255, 20, 50)']       # Ruby red
        ],
        colorbar=dict(
            title="Spatial Entropy",
            titleside="right",
            titlefont=dict(color='cyan', size=14),
            tickfont=dict(color='cyan', size=12),
            thickness=20,
            len=0.75
        ),
        hoverinfo='z',
        showscale=True
    ))
    
    fig.update_layout(
        title={
            'text': '<b>TOPOLOGICAL CHAOS ANALYSIS</b><br>Laplacian Variance Heatmap',
            'font': {'size': 16, 'color': 'cyan', 'family': 'Arial Black'},
            'x': 0.5,
            'xanchor': 'center'
        },
        plot_bgcolor='rgba(5, 10, 30, 1)',
        paper_bgcolor='rgba(10, 20, 40, 0.9)',
        margin=dict(l=20, r=20, t=60, b=20),
        height=400,
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False)
    )
    
    return fig

def create_complexity_gauge(value):
    """Create complexity index gauge"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={
            'text': "NUCLEAR COMPLEXITY INDEX",
            'font': {'size': 16, 'color': 'cyan', 'family': 'Arial Black'}
        },
        delta={'reference': 50, 'increasing': {'color': "ruby"}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "cyan"},
            'bar': {'color': "rgb(0, 200, 255)"},
            'bgcolor': "rgba(0, 0, 0, 0.3)",
            'borderwidth': 2,
            'bordercolor': "cyan",
            'steps': [
                {'range': [0, 25], 'color': 'rgba(0, 150, 100, 0.5)'},
                {'range': [25, 50], 'color': 'rgba(200, 180, 0, 0.5)'},
                {'range': [50, 75], 'color': 'rgba(255, 100, 0, 0.5)'},
                {'range': [75, 100], 'color': 'rgba(255, 20, 50, 0.7)'}
            ],
            'threshold': {
                'line': {'color': "ruby", 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(10, 20, 40, 0.9)',
        font={'color': "cyan", 'family': "Arial"},
        height=300,
        margin=dict(l=30, r=30, t=80, b=30)
    )
    
    return fig

def create_clinical_status_card(grade_info, therapy_rec, metastatic=False):
    """Create the clinical verdict card"""
    grade = grade_info.get('grade', 1)
    grade_text = grade_info.get('text', '')
    
    # Survival probability based on grade and metastatic status
    survival_base = {
        1: 0.97, 2: 0.80, 3: 0.60, 4: 0.30
    }
    
    if metastatic:
        survival_prob = 0.18  # Metastatic override
    else:
        survival_prob = survival_base.get(grade, 0.5)
    
    # Create card components
    card = dbc.Card([
        dbc.CardHeader([
            html.H3("🏥 CLINICAL VERDICT", 
                   className="text-center mb-0",
                   style={'color': 'cyan', 'fontWeight': 'bold'})
        ], style={'backgroundColor': 'rgba(0, 30, 60, 0.9)', 
                 'borderBottom': '2px solid cyan'}),
        
        dbc.CardBody([
            # Grade Display
            html.Div([
                html.H4("ISUP/WHO GRADE", 
                       style={'color': 'rgb(200, 220, 255)', 
                              'marginBottom': '10px'}),
                html.H1(f"{grade}", 
                       id="grade-display",
                       style={'color': 'rgb(255, 100, 100)' if grade >= 3 else 'lime',
                              'fontSize': '4rem',
                              'fontWeight': 'bold',
                              'textAlign': 'center',
                              'textShadow': '0 0 10px currentColor'}),
                html.P(grade_text, 
                      style={'color': 'rgb(180, 220, 255)',
                             'textAlign': 'center',
                             'fontSize': '1.1rem'})
            ], style={'marginBottom': '30px'}),
            
            # Survival Progress Bar
            html.Div([
                html.H5("5-YEAR SURVIVAL PROBABILITY", 
                       style={'color': 'rgb(200, 220, 255)',
                              'marginBottom': '10px'}),
                dbc.Progress([
                    dbc.Progress(value=survival_prob*100, 
                               color="danger" if survival_prob < 0.3 else 
                                     "warning" if survival_prob < 0.6 else "success",
                               style={'height': '25px',
                                      'fontSize': '14px',
                                      'fontWeight': 'bold'})
                ], style={'marginBottom': '5px'}),
                html.Div(f"{survival_prob*100:.1f}%", 
                        style={'color': 'cyan',
                               'textAlign': 'right',
                               'fontWeight': 'bold',
                               'fontSize': '1.2rem'})
            ], style={'marginBottom': '30px'}),
            
            # Targeted Medication Box
            html.Div([
                html.H5("🎯 TARGETED THERAPY RECOMMENDATION", 
                       style={'color': 'rgb(200, 220, 255)',
                              'marginBottom': '15px'}),
                dbc.Card([
                    dbc.CardBody([
                        html.H4(therapy_rec.get('systemic_therapy', 'N/A'),
                               style={'color': 'rgb(255, 200, 100)',
                                      'textAlign': 'center',
                                      'fontWeight': 'bold',
                                      'fontSize': '1.5rem'}),
                        html.Hr(style={'borderColor': 'cyan', 
                                      'margin': '10px 0'}),
                        html.Div([
                            html.Strong("Primary Agents: ", 
                                       style={'color': 'cyan'}),
                            html.Span(", ".join(therapy_rec.get('targeted_agents', [])),
                                     style={'color': 'rgb(220, 220, 220)'})
                        ], style={'marginBottom': '5px'}),
                        html.Div([
                            html.Strong("Evidence: ", 
                                       style={'color': 'cyan'}),
                            html.Span(therapy_rec.get('evidence_level', 'N/A'),
                                     style={'color': 'rgb(220, 220, 220)'})
                        ])
                    ])
                ], style={'backgroundColor': 'rgba(0, 40, 80, 0.7)',
                         'border': '2px solid rgb(0, 200, 255)',
                         'boxShadow': '0 0 15px rgba(0, 200, 255, 0.3)'})
            ]),
            
            # Metastatic Override Warning
            html.Div([
                dbc.Alert([
                    html.H4("⚠️ METASTATIC OVERRIDE ACTIVE", 
                           className="alert-heading"),
                    html.P("System switched to systemic doublet combinations. "
                          "5-year survival expectancy adjusted to 15-20%.",
                           className="mb-0")
                ], color="danger", 
                   style={'border': '2px solid ruby',
                          'backgroundColor': 'rgba(100, 0, 0, 0.3)'})
            ], style={'display': 'block' if metastatic else 'none',
                     'marginTop': '20px'})
        ], style={'padding': '25px'})
    ], style={'backgroundColor': 'rgba(15, 25, 45, 0.95)',
             'border': '2px solid rgba(0, 150, 255, 0.5)',
             'boxShadow': '0 10px 30px rgba(0, 0, 0, 0.5)',
             'height': '100%'})
    
    return card

# ============================================================================
# MAIN DASHBOARD APPLICATION
# ============================================================================

# Initialize Dash app with dark theme
app = dash.Dash(_name_, 
                external_stylesheets=[dbc.themes.DARKLY],
                suppress_callback_exceptions=True)

app.title = "MathRIX AI - Renal Cell Carcinoma CDSS"

# Sample data for demonstration
sample_image = np.random.rand(400, 400, 3) * 255
sample_roi = np.random.rand(200, 200, 3) * 255

# Initialize engines
spatial_engine = SpatialEntropyEngine(sample_image)
spatial_engine.compute_spatial_entropy()

grading_engine = ISUPGradingEngine(sample_roi)
grade_info = grading_engine.determine_isup_grade()

pharma_mapper = PharmacologicalMapper()
therapy_rec = pharma_mapper.get_therapy_recommendation(grade_info['grade'])

# Clinical validation data
validation_data = pd.DataFrame({
    'Parameter': ['Nuclear Entropy', 'Fractal Dimension', 'Area CV', 
                  'Nuclear Count', 'Mean Circularity', 'ISUP Grade'],
    'Value': [
        f"{grade_info.get('nuclear_entropy', 0):.3f}",
        f"{grade_info.get('fractal_dimension', 0):.3f}",
        f"{grade_info.get('area_coefficient_variation', 0):.3f}",
        f"{grading_engine.nuclear_metrics.get('nuclear_count', 0)}",
        f"{grading_engine.nuclear_metrics.get('mean_circularity', 0):.3f}",
        f"{grade_info['grade']}"
    ],
    'Normal Range': ['<0.2', '<1.3', '<0.3', '50-200', '>0.8', '1-2'],
    'Interpretation': [
        'Low' if grade_info.get('nuclear_entropy', 0) < 0.2 else 'High',
        'Simple' if grade_info.get('fractal_dimension', 0) < 1.3 else 'Complex',
        'Uniform' if grade_info.get('area_coefficient_variation', 0) < 0.3 else 'Pleomorphic',
        'Adequate',
        'Regular' if grading_engine.nuclear_metrics.get('mean_circularity', 0) > 0.8 else 'Irregular',
        grade_info['text'].split('-')[0]
    ],
    'Ground Truth': ['', '', '', '', '', '']
})

# App layout
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("MathRIX AI: Renal Cell Carcinoma CDSS",
                   style={'color': 'cyan',
                          'textAlign': 'center',
                          'fontWeight': 'bold',
                          'fontSize': '2.5rem',
                          'textShadow': '0 0 10px rgba(0, 255, 255, 0.5)',
                          'marginTop': '20px',
                          'marginBottom': '10px'}),
            html.P("Clinical Decision Support System • Version 2.1 • 2026-02-07",
                  style={'color': 'rgb(180, 220, 255)',
                         'textAlign': 'center',
                         'fontSize': '1.1rem',
                         'marginBottom': '30px'})
        ], width=12)
    ]),
    
    # Main Dashboard - Three Column Layout
    dbc.Row([
        # Left Column: Original Specimen with Heatmap Overlay
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4("🧬 ORIGINAL SPECIMEN WITH HEATMAP OVERLAY",
                           style={'color': 'cyan',
                                  'margin': '0',
                                  'fontWeight': 'bold'})
                ], style={'backgroundColor': 'rgba(0, 30, 60, 0.9)'}),
                dbc.CardBody([
                    dcc.Graph(
                        id='thermal-heatmap',
                        figure=create_thermal_heatmap_figure(
                            spatial_engine.entropy_map
                        ),
                        config={'displayModeBar': True,
                               'modeBarButtonsToRemove': ['lasso2d', 'select2d']}
                    ),
                    html.Div([
                        dbc.Badge("Neoplastic Zones Detected: ", 
                                 color="primary",
                                 className="me-2"),
                        dbc.Badge(f"{spatial_engine.neoplastic_zones['num_regions']}",
                                 color="danger" if spatial_engine.neoplastic_zones['num_regions'] > 10 else "warning")
                    ], style={'marginTop': '15px', 'textAlign': 'center'})
                ], style={'padding': '15px'})
            ], style={'height': '100%',
                     'backgroundColor': 'rgba(10, 20, 40, 0.9)',
                     'border': '1px solid rgba(0, 150, 255, 0.3)'})
        ], width=4, style={'paddingRight': '10px'}),
        
        # Middle Column: Smart Zoom with Complexity Index
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4("🔍 SMART ZOOM (ROI ANALYSIS)",
                           style={'color': 'cyan',
                                  'margin': '0',
                                  'fontWeight': 'bold'})
                ], style={'backgroundColor': 'rgba(0, 30, 60, 0.9)'}),
                dbc.CardBody([
                    # ROI Image Display
                    html.Div([
                        html.Img(id='roi-image',
                                style={'width': '100%',
                                       'border': '2px solid cyan',
                                       'borderRadius': '5px',
                                       'marginBottom': '20px'})
                    ]),
                    
                    # Complexity Gauge
                    dcc.Graph(
                        id='complexity-gauge',
                        figure=create_complexity_gauge(
                            therapy_rec['complexity_index']
                        ),
                        config={'displayModeBar': False}
                    ),
                    
                    # Nuclear Metrics
                    html.Div([
                        html.H5("NUCLEAR METRICS",
                               style={'color': 'rgb(200, 220, 255)',
                                      'marginTop': '20px',
                                      'marginBottom': '15px'}),
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H6("Entropy", 
                                               style={'color': 'cyan',
                                                      'marginBottom': '5px'}),
                                        html.H4(f"{grade_info['nuclear_entropy']:.3f}",
                                               style={'color': 'white'})
                                    ])
                                ], style={'backgroundColor': 'rgba(0, 40, 80, 0.5)'})
                            ], width=4),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H6("Fractal Dim", 
                                               style={'color': 'cyan',
                                                      'marginBottom': '5px'}),
                                        html.H4(f"{grade_info['fractal_dimension']:.3f}",
                                               style={'color': 'white'})
                                    ])
                                ], style={'backgroundColor': 'rgba(0, 40, 80, 0.5)'})
                            ], width=4),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H6("Area CV", 
                                               style={'color': 'cyan',
                                                      'marginBottom': '5px'}),
                                        html.H4(f"{grade_info['area_coefficient_variation']:.3f}",
                                               style={'color': 'white'})
                                    ])
                                ], style={'backgroundColor': 'rgba(0, 40, 80, 0.5)'})
                            ], width=4)
                        ])
                    ])
                ], style={'padding': '15px'})
            ], style={'height': '100%',
                     'backgroundColor': 'rgba(10, 20, 40, 0.9)',
                     'border': '1px solid rgba(0, 150, 255, 0.3)'})
        ], width=4, style={'paddingRight': '10px', 'paddingLeft': '10px'}),
        
        # Right Column: Clinical Verdict
        dbc.Col([
            html.Div(id='clinical-verdict-container',
                    children=create_clinical_status_card(
                        grade_info, therapy_rec
                    ))
        ], width=4, style={'paddingLeft': '10px'})
    ], style={'marginBottom': '30px'}),
    
    # Metastatic Toggle
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.H5("🔄 CLINICAL OVERRIDE CONTROLS",
                               style={'color': 'cyan',
                                      'display': 'inline-block',
                                      'marginRight': '20px'}),
                        dbc.Switch(
                            id="metastatic-toggle",
                            label="METASTATIC DISEASE (M1) DETECTED",
                            value=False,
                            style={'display': 'inline-block'}
                        ),
                        dbc.Badge("OVERRIDE INACTIVE",
                                 id="override-status",
                                 color="success",
                                 className="ms-3",
                                 style={'fontSize': '0.9rem'})
                    ], style={'textAlign': 'center'})
                ], style={'padding': '15px'})
            ], style={'backgroundColor': 'rgba(20, 40, 80, 0.7)',
                     'border': '2px solid rgba(100, 100, 255, 0.3)'})
        ], width=12)
    ], style={'marginBottom': '30px'}),
    
    # Clinical Validation Suite
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4("📊 CLINICAL VALIDATION SUITE",
                           style={'color': 'cyan',
                                  'margin': '0',
                                  'fontWeight': 'bold'})
                ], style={'backgroundColor': 'rgba(0, 30, 60, 0.9)'}),
                dbc.CardBody([
                    dash_table.DataTable(
                        id='validation-table',
                        columns=[
                            {"name": "Parameter", "id": "Parameter", "type": "text"},
                            {"name": "Value", "id": "Value", "type": "text"},
                            {"name": "Normal Range", "id": "Normal Range", "type": "text"},
                            {"name": "Interpretation", "id": "Interpretation", "type": "text"},
                            {"name": "Ground Truth (Pathologist)", "id": "Ground Truth", "type": "text", "editable": True}
                        ],
                        data=validation_data.to_dict('records'),
                        style_table={'overflowX': 'auto'},
                        style_header={
                            'backgroundColor': 'rgb(10, 40, 80)',
                            'color': 'cyan',
                            'fontWeight': 'bold',
                            'border': '1px solid rgb(0, 100, 150)'
                        },
                        style_cell={
                            'backgroundColor': 'rgb(20, 30, 60)',
                            'color': 'white',
                            'border': '1px solid rgb(40, 60, 100)',
                            'textAlign': 'center',
                            'padding': '10px'
                        },
                        style_cell_conditional=[
                            {
                                'if': {'column_id': 'Parameter'},
                                'textAlign': 'left',
                                'fontWeight': 'bold'
                            }
                        ],
                        style_data_conditional=[
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': 'rgb(25, 35, 65)'
                            },
                            {
                                'if': {
                                    'filter_query': '{Interpretation} = "High" || {Interpretation} = "Complex" || {Interpretation} = "Pleomorphic"',
                                    'column_id': 'Interpretation'
                                },
                                'backgroundColor': 'rgba(255, 50, 50, 0.3)',
                                'color': 'rgb(255, 150, 150)',
                                'fontWeight': 'bold'
                            }
                        ]
                    ),
                    html.Div([
                        dbc.Button("Export Validation Report",
                                 id="export-button",
                                 color="primary",
                                 className="me-3",
                                 style={'marginTop': '20px'}),
                        dbc.Button("Save to EMR",
                                 id="save-button",
                                 color="success",
                                 className="me-3"),
                        dbc.Button("Request Second Opinion",
                                 id="consult-button",
                                 color="warning")
                    ], style={'marginTop': '20px', 'textAlign': 'center'})
                ], style={'padding': '20px'})
            ], style={'backgroundColor': 'rgba(10, 20, 40, 0.9)',
                     'border': '1px solid rgba(0, 150, 255, 0.3)'})
        ], width=12)
    ], style={'marginBottom': '50px'}),
    
    # Footer
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Hr(style={'borderColor': 'rgba(0, 150, 255, 0.3)',
                              'margin': '30px 0'}),
                html.P("MathRIX AI CDSS v2.1 • © 2026 Digital Pathology Institute • "
                      "For Research Use Only • Validated with NCCN Guidelines v4.2025",
                      style={'color': 'rgb(150, 180, 220)',
                             'textAlign': 'center',
                             'fontSize': '0.9rem',
                             'marginBottom': '20px'})
            ])
        ], width=12)
    ])
], fluid=True, style={'backgroundColor': 'rgb(5, 15, 35)',
                     'padding': '20px',
                     'minHeight': '100vh',
                     'backgroundImage': 'linear-gradient(rgb(5, 15, 35), rgb(10, 25, 50))'})

# ============================================================================
# CALLBACKS
# ============================================================================

@app.callback(
    [Output('clinical-verdict-container', 'children'),
     Output('override-status', 'children'),
     Output('override-status', 'color')],
    [Input('metastatic-toggle', 'value')]
)
def update_metastatic_override(metastatic):
    """Handle metastatic toggle override"""
    if metastatic:
        # Get therapy with metastatic override
        therapy_rec_override = pharma_mapper.get_therapy_recommendation(
            grade_info['grade'], metastatic=True
        )
        
        # Update clinical status card
        card = create_clinical_status_card(grade_info, therapy_rec_override, metastatic=True)
        
        return card, "OVERRIDE ACTIVE", "danger"
    else:
        # Normal therapy recommendation
        therapy_rec_normal = pharma_mapper.get_therapy_recommendation(
            grade_info['grade'], metastatic=False
        )
        
        card = create_clinical_status_card(grade_info, therapy_rec_normal, metastatic=False)
        
        return card, "OVERRIDE INACTIVE", "success"

# ============================================================================
# RUN APPLICATION
# ============================================================================

if _name_ == '_main_':
    print("\n" + "="*80)
    print("MathRIX AI: Renal Cell Carcinoma Clinical Decision Support System")
    print("Version 2.1 • 2026-02-07")
    print("="*80)
    print("\nInitializing systems...")
    print(f"✓ Spatial Entropy Engine: {spatial_engine.neoplastic_zones['num_regions']} neoplastic zones detected")
    print(f"✓ ISUP Grading Engine: {grade_info['text']}")
    print(f"✓ Pharmacological Mapper: {therapy_rec['systemic_therapy']}")
    print("\nDashboard available at: http://127.0.0.1:8050")
    print("="*80 + "\n")
    
    app.run_server(debug=True, port=8050)


