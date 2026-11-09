from sklearn.svm import SVR

X = [[30], [50], [70], [100]]
y = [6.0, 9.0, 11.0, 15.0]
X_new = [[55]]

model = SVR(kernel="rbf", C=10, gamma=0.002)
model.fit(X, y)

y_pred = model.predict(X_new)

print("y_pred =", y_pred)
print("y_pred[0] =", float(y_pred[0]))
