import seaborn as sns
import matplotlib.pyplot as plt

# Load an example dataset
tips = sns.load_dataset("tips")

# Create a scatter plot with a regression line
sns.scatterplot(x="total_bill", y="tip", data=tips)
sns.regplot(x="total_bill", y="tip", data=tips, scatter=False, color="red")

# Add titles and labels
plt.title("Total Bill vs Tip")
plt.xlabel("Total Bill ($)")
plt.ylabel("Tip ($)")

# Show the plot
plt.show()
