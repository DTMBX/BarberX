using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;
using System.Text;
using Evident.Web.Services;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new() { Title = "Evident API", Version = "v1" });
    c.AddSecurityDefinition("Bearer", new()
    {
        Description = "JWT Authorization header using the Bearer scheme",
        Name = "Authorization",
        In = Microsoft.OpenApi.Models.ParameterLocation.Header,
        Type = Microsoft.OpenApi.Models.SecuritySchemeType.ApiKey,
        Scheme = "Bearer"
    });
});

// Configure CORS
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowMobileApps", policy =>
    {
        policy.WithOrigins(
            "http://localhost",
            "https://localhost",
            "capacitor://localhost",
            "ionic://localhost"
        )
        .AllowAnyMethod()
        .AllowAnyHeader()
        .AllowCredentials();
    });
});

// Configure JWT Authentication
var jwtKey = builder.Configuration["Jwt:Key"] ?? "your-secret-key-min-32-chars-long-for-security";
var jwtIssuer = builder.Configuration["Jwt:Issuer"] ?? "Evident";
var jwtAudience = builder.Configuration["Jwt:Audience"] ?? "Evident";

builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = jwtIssuer,
            ValidAudience = jwtAudience,
            IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtKey))
        };
    });

builder.Services.AddAuthorization();

// Configure HttpClient for Flask backend
var flaskBackendUrl = builder.Configuration["FlaskBackend:Url"] ?? "http://localhost:5000";
builder.Services.AddHttpClient<IAnalysisService, FlaskProxyAnalysisService>(client =>
{
    client.BaseAddress = new Uri(flaskBackendUrl);
    client.Timeout = TimeSpan.FromMinutes(10);
});

// Configure request size limits
builder.Services.Configure<Microsoft.AspNetCore.Http.Features.FormOptions>(options =>
{
    options.MultipartBodyLengthLimit = 524_288_000; // 500MB
});

builder.WebHost.ConfigureKestrel(options =>
{
    options.Limits.MaxRequestBodySize = 524_288_000; // 500MB
});

var app = builder.Build();

// Configure the HTTP request pipeline
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI(c => c.SwaggerEndpoint("/swagger/v1/swagger.json", "Evident API v1"));
}

app.UseHttpsRedirection();
app.UseCors("AllowMobileApps");
app.UseAuthentication();
app.UseAuthorization();

app.MapControllers();

// Health check endpoint
app.MapGet("/health", () => Results.Ok(new
{
    status = "healthy",
    timestamp = DateTime.UtcNow,
    version = "1.0.0",
    environment = app.Environment.EnvironmentName
}));

app.Run();
