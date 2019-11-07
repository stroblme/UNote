import numpy as np


class Kalman(object):
    def __init__(self):
        pass

    def kalman_xy(self, x, P, measurement, R, motion = np.matrix('0. 0. 0. 0.').T, Q = np.matrix(np.eye(4))):
        """
        Parameters:
        x: initial state 4-tuple of location and velocity: (x0, x1, x0_dot, x1_dot)
        P: initial uncertainty convariance matrix
        measurement: observed position
        R: measurement noise
        motion: external motion added to state vector x
        Q: motion noise (same shape as P)
        """
        return self.kalman(x, P, measurement, R, motion, Q,
                    F = np.matrix('''
                        1. 0. 1. 0.;
                        0. 1. 0. 1.;
                        0. 0. 1. 0.;
                        0. 0. 0. 1.
                        '''),
                    H = np.matrix('''
                        1. 0. 0. 0.;
                        0. 1. 0. 0.'''))

    def kalman(self, x, P, measurement, R, motion, Q, F, H):
        '''
        Parameters:
        x: initial state
        P: initial uncertainty convariance matrix
        measurement: observed position (same shape as H*x)
        R: measurement noise (same shape as H)
        motion: external motion added to state vector x
        Q: motion noise (same shape as P)
        F: next state function: x_prime = F*x
        H: measurement function: position = H*x

        Return: the updated and predicted new values for (x, P)

        See also http://en.wikipedia.org/wiki/Kalman_filter

        This version of kalman can be applied to many different situations by
        appropriately defining F and H
        '''
        # UPDATE x, P based on measurement m
        # distance between measured and current position-belief
        y = np.matrix(measurement).T - H * x
        S = H * P * H.T + R  # residual convariance
        K = P * H.T * S.I    # Kalman gain
        x = x + K*y
        I = np.matrix(np.eye(F.shape[0])) # identity matrix
        P = (I - K*H)*P

        # PREDICT x, P based on motion
        x = F*x + motion
        P = F*P*F.T + Q

        return x, P

    def initKalman(self, startPoint):
        xC = [*startPoint, 0, 0]

        self.x = np.matrix(xC).T
        self.P = np.matrix(np.eye(4))*1000 # initial uncertainty
        # self.true_x = np.linspace(0.0, 10.0, N)
        # self.true_y = true_x**2

    def applyKalman(self, observedPoints):
        # observed_x = true_x + 0.05*np.random.random(N)*self.true_x

        # observed_y = true_y + 0.05*np.random.random(N)*self.true_y

        result = []
        R = 0.01**2
        for meas in observedPoints:
            self.x, self.P = self.kalman_xy(self.x, self.P, meas, R)
            result.append((self.x[:2]).tolist())

        kalman_x, kalman_y = zip(*result)
        kalman_x_flat_list = []
        for sublist in kalman_x:
            kalman_x_flat_list.append(sublist[0])

        kalman_y_flat_list = []
        for sublist in kalman_y:
            kalman_y_flat_list.append(sublist[0])

        points = list(zip(kalman_x_flat_list, kalman_y_flat_list))
        return points