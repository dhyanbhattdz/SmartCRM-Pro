import random

class SimpleLeadPredictor:
    """Simple lead conversion predictor using business logic"""
    
    def __init__(self):
        # Define scoring weights for different factors
        self.weights = {
            'lead_source': {
                'referral': 25,
                'website': 20,
                'social_media': 15,
                'email_campaign': 10,
                'cold_call': 5,
                'other': 5
            },
            'budget_range': {
                'enterprise': 25,
                'high': 20,
                'medium': 15,
                'low': 10
            },
            'timeline': {
                'immediate': 20,
                'short': 15,
                'medium': 10,
                'long': 5
            },
            'decision_maker': {
                'yes': 25,
                'unknown': 10,
                'no': 5
            },
            'urgency_level': {
                'critical': 20,
                'high': 15,
                'medium': 10,
                'low': 5
            },
            'has_company': 10,
            'has_demo': 15,
            'has_proposal': 10,
            'competitor_mentioned': -5  # Negative weight
        }
    
    def predict_conversion(self, form_data):
        """Predict conversion probability based on form data"""
        try:
            total_score = 0
            max_possible_score = 0
            
            # Calculate score for each factor
            for factor, weight in self.weights.items():
                if factor in form_data:
                    if isinstance(weight, dict):
                        # Categorical factor
                        value = form_data[factor]
                        if value in weight:
                            total_score += weight[value]
                            max_possible_score += max(weight.values())
                    else:
                        # Boolean factor
                        if form_data[factor]:
                            total_score += weight
                        max_possible_score += weight
            
            # Add company bonus
            if form_data.get('company'):
                total_score += self.weights['has_company']
                max_possible_score += self.weights['has_company']
            
            # Calculate probability (0-100%)
            if max_possible_score > 0:
                probability = (total_score / max_possible_score) * 100
            else:
                probability = 50  # Default to 50% if no factors
            
            # Add some randomness to make it more realistic
            probability += random.uniform(-5, 5)
            probability = max(0, min(100, probability))  # Clamp between 0-100
            
            # Determine confidence level
            confidence = self._get_confidence_level(probability)
            
            # Determine conversion likelihood
            will_convert = probability > 50
            
            return {
                'probability': round(probability, 1),
                'will_convert': will_convert,
                'confidence': confidence,
                'score': total_score,
                'max_score': max_possible_score
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'probability': 50,
                'will_convert': False,
                'confidence': 'Low'
            }
    
    def _get_confidence_level(self, probability):
        """Determine confidence level based on probability"""
        if probability > 80 or probability < 20:
            return 'High'
        elif probability > 60 or probability < 40:
            return 'Medium'
        else:
            return 'Low'
    
    def get_recommendations(self, form_data, probability):
        """Generate actionable recommendations"""
        recommendations = []
        
        # Budget-based recommendations
        budget = form_data.get('budget_range')
        if budget == 'low':
            recommendations.append("💡 Consider offering a starter package or trial to increase engagement")
        elif budget == 'enterprise':
            recommendations.append("🎯 Focus on ROI demonstration and case studies from similar enterprise clients")
        
        # Timeline-based recommendations
        timeline = form_data.get('timeline')
        if timeline == 'immediate':
            recommendations.append("⚡ Prioritize this lead - immediate timeline indicates high urgency")
        elif timeline == 'long':
            recommendations.append("📅 Set up a long-term nurturing campaign with regular check-ins")
        
        # Decision maker recommendations
        decision_maker = form_data.get('decision_maker')
        if decision_maker == 'no':
            recommendations.append("🔍 Identify and connect with the actual decision maker")
        elif decision_maker == 'unknown':
            recommendations.append("❓ Research the company structure to identify decision makers")
        
        # Demo and proposal recommendations
        if not form_data.get('has_demo'):
            recommendations.append("🎬 Offer a personalized demo to showcase value")
        if not form_data.get('has_proposal'):
            recommendations.append("📄 Prepare a customized proposal based on their needs")
        
        # Lead source recommendations
        lead_source = form_data.get('lead_source')
        if lead_source == 'cold_call':
            recommendations.append("📞 Follow up with personalized content and value proposition")
        elif lead_source == 'referral':
            recommendations.append("🤝 Leverage the referral relationship for stronger credibility")
        
        # Conversion probability-based recommendations
        if probability < 30:
            recommendations.append("⚠️ Low conversion probability - focus on lead nurturing and education")
        elif probability > 70:
            recommendations.append("🎉 High conversion probability - prioritize this lead for quick closure")
        
        return recommendations
    
    def get_feature_importance(self):
        """Return feature importance for display"""
        return [
            ('Decision Maker', 25),
            ('Lead Source', 25),
            ('Budget Range', 25),
            ('Urgency Level', 20),
            ('Timeline', 20),
            ('Has Demo', 15),
            ('Has Company', 10),
            ('Has Proposal', 10),
            ('Competitor Mentioned', -5)
        ] 