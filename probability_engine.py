import random

def calculate_probability(game):
    # Simulação estatística inicial
    attack_strength = random.uniform(0.6, 1.0)
    defense_weakness = random.uniform(0.5, 1.0)

    probability = (attack_strength + defense_weakness) / 2
    return round(probability * 100, 2)
