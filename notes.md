# CroqTile · ATC’26 · 13-minute 30-second talk notes

Pacing target: 13:30 total, including slide transitions and brief pauses. The script has approximately 1,919 spoken words; at 150 words per minute, this leaves about 42 seconds for pauses. P1–P6 wording is preserved from the manually polished slides. Timing labels are rehearsal targets.

## P1 · Title · 0:00–0:20

Hi everyone, I am Heng Shi from Enflame Technology and Shanghai Jiao Tong University. I am happy here to present our work on CroqTile, a new GPU programming language designed for autonomous kernel tuning. Let us get start with the motivation.

## P2 · Operator work keeps growing · 0:20–1:15

As you can see in the figures, the bottom one shows the number of works related to operator optimization and kernel tuning, and the the larger figure shows the number of programming models, domain-specific languages, and tools emerged for writing computing kernels.

From the data, we can easily to tell two things, on the one hand, the topic about kernel tuning has draw much attention than ever before, especially for the most recent 2-3 years. On the other hand, recently emerged DSLs seems all have much higher abstraction level for programming.

To me, this two phenomenon reveals one thing. the demand for operator development has largely increased.

Why is that? we know the model architecture are actually converged into several families, like encoder, decoder and diffusion model, so why the operator optimization efforts are somehow increased

## P3 · Why kernels multiply · 1:15–2:15

I think there are four reasons stack together.

Firstly, the operators themselves keep changes. we now have much more variants of one operator than the early year of deep learning. Take attn layers as example, you now have so many variants listed here.

Secondly, we have more hardware platforms than ever before, due to the demand for computing power. just like GPGPU, TPU, PIM, DSA and so many more.

And also, even within the same device itself, it still evolves and changes. This change will lead to things like new HW features, different ISAs, new programming abstractions, and of course different sweet zone for performance.

And lastly, you may notice that the amount of fused operators today are hugely increased with the evolution of AI inference infrastructure

all these together makes the effort for writing computing kernel become so expensive.

## P4 · Kernel optimizations interact · 2:15–3:15

So of course, we would hope kernel tuning itself is not that hard. unfortunately, this is unrealistic. Let's look at how a single kenrel tuned, there will be so many things to consider. locality, bank conflict, instruction spill, memory hierarchy. For these concerns, we then designed many optimization techniques and tricks, like data Tiling, data reuse, swizzling, multibuffering, warp specialization.

So what does a optimised kernel looks like? just like this figure, you would have to find out a recipe of techniques and trick and combine them together, this recipe is never easy to find. because all these factors are coupled together, for example on GPU, a larger tile may improve locality, but can consume more shared memory per block, this will unfortunately limit the parallelism

So you can see, tradeoff is everywhere, so, how do we normally do to find this combination recipe?

## P5 · Bottleneck-driven tuning · 3:15–3:55

The first way is probably familiar to you.

We can simply start from a naive version of implementation, profile it, find out its bottleneck, and pick up a trick for this bottleneck. by make this move iteratively like a loop. you will somehow approach a near-optimal version of kernel.

We can call this bottleneck-first approach or what ever you like. and this i s how human developer normally does. no matter you are an apprentice or experts. Experts may be able to skip iterations, make multiple changes on the kernel and see further, but anyway, they still follow this workflow.

## P6 · Template search · 3:55–5:00

The second way I would like to call it search-based approach. for this way, you will find familiar names, such as autotuning and loop synthesiser. Normally, We would write a template called kernel scheme with tunable parameters, like tile size, stages, and warp count.

As the figure shows, this is a search problem in discrete space, where each point is one concrete kernel implementaion. Having this search space, you can then use algorithms you like to approaching the optimal kernel. you can do genetic search, you can do monte carlo, you can do swarm search.

This method was popular years ago, because they are the automation attempt for tuning kernels to save human efforts before AI agents pops in. and for this purpose, we also created tools for exposing more performance related factors to the syntax, and let you control. The famous name for these tools are halide IR, TVM and we call them scheduling DSL.

## P7 · Compiler transformations · 5:00–5:35

The third way is to put these optimization tricks into the compiler. As you can see here, data tiling becomes loop tiling, data reuse becomes cache staging, and multibuffering becomes software pipelining.

So we can describe a schedule, or let compiler passes apply these transformations. This is where tools like TVM and MLIR come in. But there is still human effort behind it. When new hardware needs a new kernel structure, somebody has to teach the compiler how to make that transformation.

## P8 · Agents rewrite the kernel · 5:35–6:20

So now, with coding agents, we have another way to do this. Remember the bottleneck-first approach? We can put an agent into that loop, let it read the kernel, look at the profiler feedback, and pick up a trick to try.

The agent can change both the parameters and the kernel structure. And of course, there are many efforts on planning, evaluation, tools and knowledge, as listed here.

In our work, we want to design an agent-specific kernel language, which serves as the programming substrate for this loop. It should help the agent express its optimization ideas, implement the changes, and do better tuning.

## P9 · Design for agent failures · 6:20–7:05

To achieve this target, we have to understand the typical failure modes for tuning agents.

Firstly, the context gets used up very quickly. We keep adding code, profiler output and debugging messages. After several rounds, the agent may lose earlier attempts and repeat something it already tried.

Secondly, one optimization may need changes in many places. Take TMA as an example, the descriptor, swizzle, copy and synchronization have to work together. Missing one can break the kernel.

And lastly, the feedback can be hard to use. If the GPU just hangs, how does the agent know which statement to fix?

So these are the problems we want our language and compiler to address.

## P10 · CroqTile: two co-design axes · 7:05–7:45

When we try to meet these needs, we run into an impossible triangle: expressiveness, performance and development efficiency. We want enough freedom to tune, fast kernels, and low effort for each iteration.

CUDA and CuTe give us control and performance, but require a lot of code. Tile languages make programming easier, while hiding some structural choices that matter for tuning.

So our choice is to keep the performance controls explicit, and reduce the work around them. We do this along two axes: syntax–context co-design, to make the code compact for the agent; and compiler–harness co-design, to make failures easier to identify and repair.

## P11 · Compact syntax preserves context · 7:45–8:25

Let us look at the syntax–context part first. Here, we try to increase the information density as much as possible, so the agent can express an optimization with less code.

This matters because the context has to hold much more than the source. We have skills and system prompts, profiler and compiler feedback, and we also need room for the agent's thinking.

And notably, if a bug emerges, many of these costs are multiplied. The agent reads the code again, gets more feedback, and spends more of its thinking budget on the repair.

So compact syntax saves room for the whole tuning process.

## P12 · parallel: one construct, three levels · 8:25–9:10

So how do we simplify the syntax without sacrificing performance? We first identify the routine setup code and verify that it can be derived from the chosen parallel structure.

As you can see in the parallel example here, the work division and execution level stay explicit. The compiler handles the corresponding indexing and launch setup, so the agent does not have to write those details by hand.

## P13 · tma: one statement per transfer · 9:10–9:45

Then there are operations that affect performance but follow a clear optimization pattern. Take TMA data movement as an example.

Here, the agent specifies which tile moves where, while the compiler generates the descriptor and transfer setup. But the best swizzle pattern still needs tuning, so we keep those options explicit as modifiers in the syntax.

## P14 · Compile success across shapes · 9:45–10:20

So does this help the agent produce a program that compiles? Under the same agent, hardware and budget, CroqTile reaches 85.7 percent on the first attempt for static shapes. For dynamic shapes, it stays at 82.1 percent, compared with 48 percent for Triton in this evaluation.

Two things contribute here: fewer coupled edits in the syntax, and symbolic inference to work out shape relationships.

Of course, compiling successfully does not mean the result is correct. We still verify correctness, but fewer compile repairs leave more time for tuning.

## P15 · Diagnostics that guide repair · 10:20–11:05

And when compilation does fail, what should we return to the agent? This brings us to the compiler and harness.

We check shapes and resource limits before launch, and use runtime assertions for constraints that depend on runtime values.

Let us follow the example on the left. The feedback tells us which constraint failed, what values we observed, where the statement is, and how to repair it. Here, the dimensions do not match, and the suggested repair is to add zero fill for the tail tile.

So the agent has a concrete next move: go to that statement, make the change, and compile again.

## P16 · Prune before GPU execution · 11:05–11:45

These checks also help us narrow the search before using the GPU. Candidates that exceed resource limits can be rejected early, with feedback telling the agent what to change.

As you can see here, many invalid configurations are removed at this stage. The harness then checks correctness and measures performance for the remaining candidates.

So the compiler is part of the tuning loop: it helps the agent spend less time debugging invalid programs and more time finding faster kernels.

## P17 · Close the autonomous loop · 11:45–12:25

Now let us put these pieces back into the tuning loop. The agent profiles, proposes a change, implements it, compiles, measures, and decides whether to keep it.

If compilation fails, the feedback goes back for repair. If it passes, we check correctness and measure performance. Skills and references provide the language rules and optimization ideas along the way.

So this is still the iterative workflow we started with. Across the evaluated workloads with vendor references, the resulting kernels achieve a geometric-mean speedup of 1.23 times. Let us look at two examples.

## P18 · Tuning beyond cuBLAS · 12:25–13:00

As you can see on the left, this is dense FP16 GEMM at 16,384 cubed. The solid lines show the best throughput found so far, and the dashed line is cuBLAS. CroqTile gradually improves, reaches that line, and then goes beyond it.

On the right, for block-scale E4M3 GEMM at 8,192 cubed, it crosses the vendor baseline earlier and keeps improving.

Both use the same agent and per-shape time cap on H800. So in these two cases, the agent can keep turning its changes into working, faster kernels.

## P19 · Thank you · 13:00–13:30

So the main idea is to make the language and compiler fit this iterative tuning process. Compact code helps the agent keep its history, explicit controls let it try optimizations, and useful feedback helps it repair mistakes.

CroqTile is open source, and you can see five accepted works using it here. Please feel free to scan the code and have a look.

That is all from me. Thank you, and happy to take your questions.
