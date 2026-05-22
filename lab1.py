h, m, s = 8, 40, 30 

h_pos =  30*h + 0.5*m + (0.5 / 60)*s
m_pos = 6*m + 0.1*s 
angle = abs(h_pos - m_pos)

print("Кут між стрілками:",angle)