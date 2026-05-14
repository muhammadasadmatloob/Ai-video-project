declare module 'maath/random/dist/maath-random.esm' {
  /**
   * Generates random points inside a sphere.
   * @param buffer The Float32Array to fill.
   * @param options Configuration for the sphere.
   */
  export function inSphere(
    buffer: Float32Array, 
    options: { radius: number }
  ): Float32Array;

  
}
