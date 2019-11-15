import numpy as np
from scipy.signal import savgol_filter
from scipy.linalg import lstsq
from scipy import dot

def tuplesToArrays(points):
    xPoints = []
    yPoints = []

    for point in points:
        xPoints.append(point[0])
        yPoints.append(point[1])

    return xPoints, yPoints

def arraysToTuples(xPoints, yPoints):
    points = []

    for xPoint, yPoint in zip(xPoints, yPoints):
        points.append([xPoint, yPoint])

    return points

class FormEstimator(object):
    def __init__(self):
        super().__init__()

        ransac = Ransac()

    def estimateForm(self, observedPoints):
        pass

    def estimateLine(self, observedPoints):
        n_inputs = 1
        n_outputs = 1

        xPoints, yPoints = tuplesToArrays(observedPoints)
        A_exact = np.array(xPoints)
        B_exact = np.array(yPoints)
        all_data = np.hstack( (A_exact,B_exact) )

        # setup model

        input_columns = range(n_inputs) # the first columns of the np.array
        output_columns = [n_inputs+i for i in range(n_outputs)] # the last columns of the np.array
        model = LinearLeastSquaresModel(input_columns,
                                        output_columns)

        MINNUMBEROFDATAPOINTS = 50
        MINNUMBEROFITERATIONS = 1000
        THRESPOINTSFITWELL = 7e3
        CLOSEDATAPOINTSFORWELLFITTING = 300

        # run RANSAC algorithm
        ransac_fit, ransac_data = self.ransac(all_data,model,
                                        MINNUMBEROFDATAPOINTS,
                                        MINNUMBEROFITERATIONS,
                                        THRESPOINTSFITWELL,
                                        CLOSEDATAPOINTSFORWELLFITTING, # misc. parameters
                                        debug=False,
                                        return_all=True)
        return ransac_data


class Kalman(object):

    def __init__(self):
        super().__init__()

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

    def applyKalman(self, observedPoints):
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

class Savgol(object):

    def __init__(self):
        super().__init__()

    def initSavgol(self):
        pass




    def applySavgol(self, observedPoints):
        WINDOW_LENGTH = 19 #odd!
        POLYNOM_GRADE = 2

        xPoints, yPoints = tuplesToArrays(observedPoints)

        if len(observedPoints) > WINDOW_LENGTH:
            xPointsS = savgol_filter(xPoints, WINDOW_LENGTH, POLYNOM_GRADE)
            yPointsS = savgol_filter(yPoints, WINDOW_LENGTH, POLYNOM_GRADE)

            points = arraysToTuples(xPointsS, yPointsS)

        else:
            points = observedPoints

        return points

class Ransac():
    def __init__(self):
        super().__init__()

    def applyRansac(data,model,n,k,t,d,debug=False,return_all=False):
        """
        Fit model parameters to data using the RANSAC algorithm
        """
        iterations = 0
        bestfit = None
        besterr = np.inf
        best_inlier_idxs = None
        while iterations < k:
            maybe_idxs, test_idxs = random_partition(n,data.shape[0])
            maybeinliers = data[maybe_idxs,:]
            test_points = data[test_idxs]
            maybemodel = model.fit(maybeinliers)
            test_err = model.get_error( test_points, maybemodel)
            also_idxs = test_idxs[test_err < t] # select indices of rows with accepted points
            alsoinliers = data[also_idxs,:]
            if len(alsoinliers) > d:
                betterdata = np.concatenate( (maybeinliers, alsoinliers) )
                bettermodel = model.fit(betterdata)
                better_errs = model.get_error( betterdata, bettermodel)
                thiserr = np.mean( better_errs )
                if thiserr < besterr:
                    bestfit = bettermodel
                    besterr = thiserr
                    best_inlier_idxs = np.concatenate( (maybe_idxs, also_idxs) )
            iterations+=1
        if bestfit is None:
            raise ValueError("did not meet fit acceptance criteria")
        if return_all:
            return bestfit, {'inliers':best_inlier_idxs}
        else:
            return bestfit

    def random_partition(n,n_data):
        """return n random rows of data (and also the other len(data)-n rows)"""
        all_idxs = np.arange( n_data )
        np.random.shuffle(all_idxs)
        idxs1 = all_idxs[:n]
        idxs2 = all_idxs[n:]
        return idxs1, idxs2

class LinearLeastSquaresModel:
    """linear system solved using linear least squares

    This class serves as an example that fulfills the model interface
    needed by the ransac() function.

    """
    def __init__(self,input_columns,output_columns,debug=False):
        self.input_columns = input_columns
        self.output_columns = output_columns
        self.debug = debug
    def fit(self, data):
        A = np.vstack([data[:,i] for i in self.input_columns]).T
        B = np.vstack([data[:,i] for i in self.output_columns]).T
        x,resids,rank,s = lstsq(A,B)
        return x
    def get_error( self, data, model):
        A = np.vstack([data[:,i] for i in self.input_columns]).T
        B = np.vstack([data[:,i] for i in self.output_columns]).T
        B_fit = dot(A,model)
        err_per_point = np.sum((B-B_fit)**2,axis=1) # sum squared error per row
        return err_per_point
