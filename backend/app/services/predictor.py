from app.schemas import Factor, PredictionResponse, Profile, Readiness, Suggestion


class MockPredictor:
    version = "mock-v1"

    def predict(self, profile: Profile) -> PredictionResponse:
        scores = [profile.ssc_p, profile.hsc_p, profile.degree_p, profile.etest_p]
        base = sum(scores) / len(scores)
        experience_bonus = 4 if profile.workex == "Yes" else 0
        project_bonus = min((profile.project_count or 0) * 2, 8)
        probability = max(0.05, min(0.95, (base + experience_bonus + project_bonus) / 100))
        score = round(probability * 100)
        level = "Ready" if score >= 75 else "Promising" if score >= 55 else "Building"
        factors = [
            Factor(label="Degree performance", direction="positive" if profile.degree_p >= 65 else "focus", value=f"{profile.degree_p:.0f}%"),
            Factor(label="Aptitude readiness", direction="positive" if profile.etest_p >= 65 else "focus", value=f"{profile.etest_p:.0f}%"),
            Factor(label="Project depth", direction="positive" if (profile.project_count or 0) >= 2 else "focus", value=f"{profile.project_count or 0} projects"),
        ]
        suggestions = []
        if profile.etest_p < 65:
            suggestions.append(Suggestion(title="Practice aptitude in short sprints", reason="Build consistency with timed tests and review your weak areas."))
        if (profile.project_count or 0) < 2:
            suggestions.append(Suggestion(title="Build one stronger project", reason="Show depth with a deployed or well-documented project."))
        if (profile.coding_problems_solved or 0) < 100:
            suggestions.append(Suggestion(title="Create a coding routine", reason="A small, repeatable problem-solving habit compounds over time."))
        if not suggestions:
            suggestions.append(Suggestion(title="Keep building evidence", reason="Document outcomes from your projects, practice, and internships."))
        return PredictionResponse(
            prediction="Placed" if probability >= 0.5 else "Not Placed",
            probability=round(probability, 2),
            readiness=Readiness(level=level, score=score, summary="A directional estimate to help you choose your next step."),
            factors=factors,
            suggestions=suggestions,
            disclaimer="This is an estimate for learning and preparation, not a guarantee of employment.",
            modelVersion=self.version,
        )
