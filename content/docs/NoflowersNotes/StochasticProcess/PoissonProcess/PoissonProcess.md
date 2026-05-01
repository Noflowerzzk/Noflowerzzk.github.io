
## Poisson distribution and Exponent distribution

$X \sim \operatorname{Pois}(\lambda)$ iff for all $k \in \mathbb{N}, \mathbb{P}[X = k] = \dfrac{\lambda^k}{k!}\mathrm{e}^{-\lambda}$

**Poisson distribution** has such property:

$X_1 \sim \operatorname{Pois}(\lambda_1), X_2 \sim \operatorname{Pois}(\lambda_2)$, then $X_1 + X_2 \sim \operatorname{Pois}(\lambda_1 + \lambda_2)$

!!! examples "Guests in a restaurant"

    We assume we divide a day into $n$ parts and each part is small enough that at most one guest can enter the restaurant with the probability $p$.  
    Let $X_i = \mathbf{1}[\text{Guest entered at time part }i]$, then $X_i \sim \operatorname{Ber}(p)$, $\displaystyle Z_n = \sum_{i = 1}^nX_i$, $Z_n \sim \operatorname{Binom}(n, p)$.

    Now we let $n \to \infty$, $Z_n \sim \operatorname{Pois}(np)$.

$X \sim \operatorname{Exp}(\lambda)$, then

$$
f(x) = \begin{cases}
    \lambda \mathrm{e}^{-\lambda x}, &x \geq 0 \\
    0, & x < 0
\end{cases}
$$

and $\mathbb{E}X = \dfrac{1}{\lambda}, \operatorname{Var}X = \dfrac{1}{\lambda^2}$

And we have the properties as below:

$$
    \mathbb{P}[X > t + s | X > s] = \mathbb{P}[X > t]
$$

$$
    X_1 \sim \operatorname{Exp}(\lambda_1), X_2 \sim \operatorname{Exp}(\lambda_2) \Rightarrow X_1 \land X_2 \sim \operatorname{Exp}(\lambda_1 + \lambda_2)
$$

$$
    \mathbb{P}[X_1 < X_2] = \frac{\lambda_1}{\lambda_1 + \lambda_2}
$$

## Poisson Process

We call a sequence of random variables $\{N(s)\}_{s\geq 0}$ a **Poisson process** iff.

1. $N(0) = 0$  
2. for all $t, s \geq 0$, $N(t + s) - N(s) \sim \operatorname{Pois}(\lambda t)$  
3. for all $t_0 \leq t_1 \leq \ldots \leq t_n$, $N(t_{i}) - N(t_{i - 1})$ are mutually independent.

### Describe Poisson process with Exponent distribution

Let $\tau_1, \tau_2, \ldots, \tau_n$ be a sequence of independent variables following exponent distribution, $\tau_i \sim \operatorname{Exp}(\lambda)$. Let $\displaystyle T_n = \sum_{i = 1}^n\tau_i$, and for $t \geq 0$, define $N(t) := \max \{n | T_n \leq t\}$, then $\{N(t)\}$ is a Poisson process.

!!! normal-comment "Intuitive understanding"

    $\tau_i$ is the time between the arrival of guests $i - 1$ and $i$, and $T_n$ is the arrival time of guest $n$, $N(t)$ is the number of guests arrived at time $t$

!!! remarks "Proof"

    (To be completed...)


## Thinning of Poisson process

We say two Poisson process $N_1(t), N_2(t)$ independent iff for all $t_0 \leq t_1 \leq \ldots \leq t_n$, $\displaystyle \bigcup_{i \in [N]}\{N_1(t_i) - N_1(t_{i - 1}), N_2(t_i) - N_2(t_{i - 1})\}$ are independent.

In the guests case, we divide the guests into some types randomly, which is decided by a variable $Y_i$ for guest $i$, and $p_k = \mathbb{p}[Y_i = k]$. Now let $N_k(t)$ be the number of guests of type $k$ at time $t$. We call $\{N_k(t)\}_{t \geq 0}$ be a thinning of the Poisson process. 

For all $k$, $\{N_k(t)\}_{t \geq 0}$ is a Poisson process of $\lambda p_k$, and they are mutually independent.

!!! remarks "Proof"

    (To be completed...)

## Poisson Approximation

### Balls into Bins 

Throw $m$ balls into $n$ bins and $X_i$ is the number of balls in box $i$. Then $X_i \sim \operatorname{Binom}(m, 1/n)$.

$Y_i \sim \operatorname{Pois}(\lambda)$ are independent Poisson distribution. If we conditioned at $\displaystyle\sum_{i = 1}^nY_i = m$, then $(Y_1, \ldots, Y_n)$ and $(X_1, \ldots, X_n)$ has the same distribution. (**Poisson Approximation Theorem**)

!!! remarks "Proof"

    For all $(a_1, \ldots, a_n)$ s.t. $\displaystyle\sum_{i = 1}^n a_i = m$, 

    $$
    \mathbb{P}[(X_1, \ldots, X_n) = (a_1, \ldots, a_n)] = \frac{1}{n^m}\frac{m!}{a_1!a_2!\ldots a_n!}
    $$

    Also

    $$
    \begin{aligned} 
        &\mathbb{P}\left[(X_1, \ldots, X_n) = (a_1, \ldots, a_n)\Bigg|\sum_{i = 1}^nY_i = m\right] &= \frac{\prod_{i = 1}^n\mathbb{P}[Y_i = a_i]}{\mathbb{P}\left[\sum_{i = 1}^nY_i = m\right]} \\
        &= \frac{\prod_{i = 1}^n\mathrm{e}^{-\lambda}\frac{\lambda^{a_i}}{a_i!}}{\mathrm{e}^{-\lambda n}\frac{(\lambda n)^m}{m!}} = \frac{1}{n^m}\frac{m!}{a_1!a_2!\ldots a_n!}
    \end{aligned}   
    $$

